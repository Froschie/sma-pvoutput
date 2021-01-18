# first build Alpine Base Image with Init
FROM alpine:latest
ARG arch
ENV arch=${arch}
RUN apk add --no-cache bash curl tzdata
ADD https://github.com/just-containers/s6-overlay/releases/latest/download/s6-overlay-${arch}.tar.gz /tmp/s6overlay.tar.gz
RUN tar xfz /tmp/s6overlay.tar.gz -C / && rm /tmp/s6overlay.tar.gz
ENTRYPOINT ["/init"]

# Image Description
LABEL version="1.0" description="Script to Query data from SMA InfluxDB and store it to pvoutput.org."

# Install Python
RUN apk add --no-cache python3 py-pip

# Install required Python Modules
RUN pip install influxdb requests

# Define Environment Variables needed for Script
ENV pv_key="abc" pv_sid="12345" pv_consumption=0 influx_ip="192.168.1.3" influx_port="8086" influx_user="user" influx_pw="pw" influx_db="SMA"

# Startup Script to Container
RUN mkdir -p /etc/services.d/pv-output
COPY ./run /etc/services.d/pv-output/run

# Python Script to Container
COPY ./pvoutput.py /pvoutput.py
