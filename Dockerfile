FROM python:slim

# Image Description
LABEL version="1.0" description="Script to Query data from SMA InfluxDB and store it to pvoutput.org."

# Install required Python Modules
RUN pip install influxdb requests

# Install pgrep for stopping the Python Script in case needed
RUN apt-get update && apt-get install -y procps htop dos2unix

# Define Environment Variables needed for Script
ENV pv_key="abc" pv_sid="12345" pv_consumption=0 influx_ip="192.168.1.3" influx_port="8086" influx_user="user" influx_pw="pw" influx_db="SMA"

# Set correct Timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# Copy Scripts to Container
ADD ./pvoutput.py /pvoutput.py
ADD ./start.sh /start.sh
RUN chmod +x /start.sh && dos2unix /start.sh

# Default Command for starting the Container
CMD ["/start.sh"]