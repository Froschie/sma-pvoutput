#!/bin/bash
python -u /pvoutput.py --pv_key $pv_key --pv_sid $pv_sid --pv_consumption $pv_consumption --influx_ip $influx_ip --influx_port $influx_port --influx_user $influx_user --influx_pw $influx_pw --influx_db $influx_db &

child=$(pgrep -P $$)
echo "Python Script started as process: " $child

cleanup() {
    echo "Stopping Python Script" $child
    kill -TERM $child
    sleep 5s
    exit
}

trap cleanup INT TERM

while :; do
    sleep 1s
done