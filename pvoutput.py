# encoding: utf-8
import json
import time
from datetime import datetime, timedelta, date
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from influxdb import InfluxDBClient
import argparse
import sys
import logging
import pytz
tz = pytz.timezone('Europe/Berlin')

parser=argparse.ArgumentParser(
    description='''Upload SMA values to PV Output.''')
parser.add_argument('--pv_key', type=str, required=True, default="", help='PV OutPut API Key.')
parser.add_argument('--pv_sid', type=str, required=True, default="", help='PV Output System ID.')
parser.add_argument('--pv_consumption', type=int, required=False, default=0, choices=[0, 1], help='Upload of Power Consumption to PV Output?')
parser.add_argument('--influx_ip', type=str, required=True, default="", help='IP of the Influx DB Server.')
parser.add_argument('--influx_port', type=str, required=True, default="", help='Port of the Influx DB Server.')
parser.add_argument('--influx_user', type=str, required=True, default="", help='User of the Influx DB Server.')
parser.add_argument('--influx_pw', type=str, required=True, default="", help='Password of the Influx DB Server.')
parser.add_argument('--influx_db', type=str, required=True, default="", help='DB name of the Influx DB Server.')
parser.add_argument('--log', type=str, required=False, default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help='Specify Log output.')
args=parser.parse_args()

# Log Output configuration
logging.basicConfig(level=getattr(logging, args.log), format='%(asctime)s.%(msecs)05d %(levelname)07s:\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)

log.debug("Used Arguments: " + str(args))

# Time Rounding Function
def ceil_time(ct, delta):
    return ct + (datetime.min - ct) % delta

now = datetime.now()
new_time = ceil_time(now, timedelta(seconds=300))

log.info("Actual Time: " + str(now) + " waiting for: " + str(new_time))

# Wait for Full Minute / Half Minute
while now < new_time:
    time.sleep(0.5)
    now = datetime.now()
time.sleep(10)

client = InfluxDBClient(host=args.influx_ip, port=args.influx_port, username=args.influx_user, password=args.influx_pw)

def pv_limit(key, sid):
    url = "https://pvoutput.org/service/r2/getstatus.jsp"
    payload = {}
    headers = {
        'X-Rate-Limit': '1',
        'X-Pvoutput-Apikey': key,
        'X-Pvoutput-SystemId': sid
    }
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.headers['X-Rate-Limit-Reset']

def pv_wait(key, sid):
    pv_waittime = int(pv_limit(key, sid))+10
    now = int(datetime.now().timestamp())
    log.warning("PV Output Limit reached, waiting for {} s.".format(pv_waittime-now))
    while now < pv_waittime:
        time.sleep(1)
        now = int(datetime.now().timestamp())

def pv_status(key, sid):
    url = "https://pvoutput.org/service/r2/getstatus.jsp"
    payload = {}
    headers = {
        'X-Rate-Limit': '1',
        'X-Pvoutput-SystemId': sid,
        'X-Pvoutput-Apikey': key
    }
    response = requests.request("GET", url, headers=headers, data = payload)
    log.debug(response.text.encode('utf8'))
    if response.status_code == 403:
        pv_wait(key, sid)
        response = requests.request("GET", url, headers=headers, data = payload)
        log.debug(response.text.encode('utf8'))
    if response.status_code == 400:
        for day in range(1, int(response.headers['X-Rate-Limit-Remaining'])-5):
            d = date.today() - timedelta(days=day)
            url = "https://pvoutput.org/service/r2/getstatus.jsp?d={}".format(d.strftime('%Y%m%d'))
            response = requests.request("GET", url, headers=headers, data = payload)
            log.debug(response.text.encode('utf8'))
            if response.status_code == 200:
                break
        if response.status_code != 200:
            pv_dict = {
                'pv_year': d.strftime('%Y'),
                'pv_month': d.strftime('%m'),
                'pv_day': d.strftime('%d'),
                'pv_hour': 0,
                'pv_min': 0,
                'pv_unixtime': time.mktime(d.timetuple())
            }
            return pv_dict
    pv_values = response.text.split(",")
    pv_year = int(pv_values[0][:4])
    pv_month = int(pv_values[0][4:6])
    pv_day = int(pv_values[0][6:8])
    pv_hour = int(pv_values[1][:2])
    pv_min = int(pv_values[1][3:5])
    pv_unixtime = int(datetime(pv_year, pv_month, pv_day, pv_hour, pv_min).timestamp())
    pv_dict = {
        'pv_year': pv_year,
        'pv_month': pv_month,
        'pv_day': pv_day,
        'pv_hour': pv_hour,
        'pv_min': pv_min,
        'pv_unixtime': pv_unixtime
    }
    return pv_dict

pv_status_values = pv_status(args.pv_key, args.pv_sid)
log.info("Last PV Output Value: {}:{} {}.{}.{}".format(pv_status_values['pv_hour'], pv_status_values['pv_min'], pv_status_values['pv_day'], pv_status_values['pv_month'], pv_status_values['pv_year']))

# Execute Query every Xs
try:
    while True:
        log.info("Querying SMA Values from Influx from Timestamp " + str(pv_status_values['pv_unixtime']))
        # Connect to InfluxDB and save Solar Values
        try:
            client = InfluxDBClient(host=args.influx_ip, port=args.influx_port, username=args.influx_user, password=args.influx_pw)
            client.switch_database(args.influx_db)

            # Query Latest Data of Solar Generation
            solar_data = {}
            solar_watt = 0
            consumption_watt = 0
            solar_total = client.query('SELECT max(solar_total) FROM totals WHERE  time >= %ss GROUP BY time(5m) tz(\'Europe/Berlin\')' % (pv_status_values['pv_unixtime']-3600), epoch="s").get_points()
            for point in solar_total:
                if point['max'] is not None:
                    if point['time']+300 not in solar_data:
                        solar_data[point['time']+300] = {}
                    if point['max']+300 is not None:
                        solar_data[point['time']+300]['solar'] = int(point['max'])
            consumption_total = client.query('SELECT max(consumption_total) FROM totals WHERE time >= %ss GROUP BY time(5m) tz(\'Europe/Berlin\')' % (pv_status_values['pv_unixtime']-3600), epoch="s").get_points()
            for point in consumption_total:
                if point['max'] is not None:
                    if point['time']+300 not in solar_data:
                        solar_data[point['time']+300] = {}
                    if point['max']+300 is not None:
                        solar_data[point['time']+300]['consumption'] = int(point['max'])
            for point in solar_data:
                if point > pv_status_values['pv_unixtime']:
                    if "solar" in solar_data[point] and "consumption" in solar_data[point]:
                        if int(time.time()) < point:
                            break
                        if point-300 in solar_data:
                            solar_watt = int((solar_data[point]['solar']-solar_data[point-300]['solar'])/5*60)
                            consumption_watt = int((solar_data[point]['consumption']-solar_data[point-300]['consumption'])/5*60)
                        ts = datetime.fromtimestamp(point)
                        if args.pv_consumption:
                            url = "https://pvoutput.org/service/r2/addstatus.jsp?d=%s&t=%s&v1=%s&v2=%s&v3=%s&v4=%s&c1=1" % (ts.strftime('%Y%m%d'), ts.strftime('%H:%M'), solar_data[point]['solar'], solar_watt, solar_data[point]['consumption'], consumption_watt)
                        else:
                            url = "https://pvoutput.org/service/r2/addstatus.jsp?d=%s&t=%s&v1=%s&v2=%s&c1=1" % (ts.strftime('%Y%m%d'), ts.strftime('%H:%M'), solar_data[point]['solar'], solar_watt)
                        payload = {}
                        headers = {
                            'X-Pvoutput-Apikey': args.pv_key,
                            'X-Pvoutput-SystemId': args.pv_sid
                        }
                        response = requests.request("POST", url, headers=headers, data = payload)
                        if response.status_code == 403:
                            pv_wait(args.pv_key, args.pv_sid)
                            response = requests.request("POST", url, headers=headers, data = payload)
                        if response.status_code == 200:
                            if args.pv_consumption == 1:
                                log.info("PV Output data added for {} with values {} Wh / {} W for solar and {} Wh / {} W for consumption.".format(ts.strftime('%H:%M %d.%m.%Y'), solar_data[point]['solar'], solar_watt, solar_data[point]['consumption'], consumption_watt))
                            else:
                                log.info("PV Output data added for {} with value {} Wh / {} W for solar. ".format(ts.strftime('%H:%M %d.%m.%Y'), solar_data[point]['solar'], solar_watt))
                            pv_status_values['pv_unixtime'] = point
                        else:
                            log.error("PV Output data adding failed with code: {} and text: {}.".format(response.status_code, response.text))
        except Exception as e:
            log.error("InfluxDB error.")
            log.error(e)
        finally:
            client.close()
        time.sleep(300 - ((time.time() - new_time.timestamp()) % 300)+10)
except KeyboardInterrupt:
    log.info("Script aborted...")
finally:
    log.info("Script Ended.")
