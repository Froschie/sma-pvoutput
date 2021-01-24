# sma-pvoutput ![Docker Image CI](https://github.com/Froschie/sma-pvoutput/workflows/Docker%20Image%20CI/badge.svg)
Script to upload SMA data to pvoutput.org Website.

## Start Docker Container  

Pull latest Image:  
`docker pull froschie/sma-pvoutput:latest`  

Start Container:  
```
docker run -it \
 -e influx_ip=192.168.1.3 \
 -e influx_port=8086 \
 -e influx_db=SMA \
 -e influx_user=user \
 -e influx_pw=pw \
 -e pv_consumption=0 \
 -e pv_sid=PV Output System ID \
 -e pv_key=PV OutPut API Key \
 -e TZ=Europe/Berlin \
 froschie/sma-pvoutput
```
*Note: please adapt the parameters as needed and replace "-it" with "-d" to run it permanently or use docker-compose!*  


## Start Docker Container via Docker-Compose  
```bash
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/docker-compose.yaml
vi docker-compose.yaml
docker-compose up -d
```
*Note: please adapt the parameters as needed!*


## Create Docker Container Manually

```bash
mkdir sma-pvoutput
cd sma-pvoutput/
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/Dockerfile
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/run
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/pvoutput.py
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/s6download.sh
docker build --tag=sma-pvoutput .
```
