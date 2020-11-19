# sma-pvoutput
Script to upload SMA data to pvoutput.org Website.


## Create Docker Container

```bash
mkdir sma-pvoutput
cd sma-pvoutput/
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/Dockerfile
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/start.sh
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/pvoutput.py
docker build --tag sma-pvoutput .
```


## Start Docker Container via Docker-Compose File
```bash
curl -O https://raw.githubusercontent.com/Froschie/sma-pvoutput/main/docker-compose.yaml
vi docker-compose.yaml
docker-compose up -d
```
*Note: please adapt the parameters in <> brackets, use external folder to save the database and use matching values in the WeMos configuration! Don´t override your existing docker compose file!*
