# first build Alpine Base Image with Init
FROM alpine:3.12
ARG TARGETPLATFORM
RUN apk add --no-cache bash curl tzdata
COPY ./s6download.sh /s6download.sh
RUN chmod +x /s6download.sh && bash /s6download.sh && tar xfz /tmp/s6overlay.tar.gz -C / && rm /tmp/s6overlay.tar.gz && rm /s6download.sh
ENTRYPOINT ["/init"]

# Image Description
LABEL version="2.1" description="Script to Query data from SMA InfluxDB and store it to pvoutput.org."

# Install Python and Python Modules
RUN apk add --no-cache python3 py-pip && pip install influxdb requests && apk del py-pip

# Define Environment Variables needed for Script
ENV pv_key="abc" pv_sid="12345" pv_consumption=0 influx_ip="192.168.1.3" influx_port="8086" influx_user="user" influx_pw="pw" influx_db="SMA"

# Startup Script to Container
RUN mkdir -p /etc/services.d/pv-output
COPY ./run /etc/services.d/pv-output/run

# Python Script to Container
COPY ./pvoutput.py /pvoutput.py
