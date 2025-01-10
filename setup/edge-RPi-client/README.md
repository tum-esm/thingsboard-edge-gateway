# OS Setup

- Install RASPBERRY PI OS LITE (64-Bit)
- Setup SSH, WIFI, Hostname
- Copy config.txt into bootfs folder on SD card

```
sudo apt update
sudo apt upgrade
sudo apt install -y build-essential libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev openssl docker.io git tldr ncdu minicom pigpio libsqlite3-dev wget screen udhcpc
```

# Python

```
wget https://www.python.org/ftp/python/3.12.8/Python-3.12.8.tgz
sudo tar zxf Python-3.12.8.tgz
cd Python-3.12.8
sudo ./configure --enable-optimizations --enable-loadable-sqlite-extensions
sudo make -j 4
sudo make install
curl -sSL https://install.python-poetry.org/ | python3.12 -
```

# Modem

## AT Modem Commands

```
# open modem interface
sudo minicom -D /dev/ttyS0
# check modem functionality
AT
# see terminal input
ATE1
# switch to RNDIS
AT+CUSBPIDSWITCH=9001,1,1

# Wait for a possible modem restart

# set SIM APN
AT+CGDCONT=1,"IP","iotde.telefonica.com"
# set network registration to automatic
AT+COPS=0
# set LTE only
AT+CNMP=38
```

## Install Driver

```
# download and install driver
cd /home/pi
wget https://www.waveshare.net/w/upload/8/89/SIM8200_for_RPI.7z
7z x SIM8200_for_RPI.7z -r -o./SIM8200_for_RPI
sudo chmod 777 -R SIM8200_for_RPI
cd SIM8200_for_RPI/Goonline
make clean
make

# Set DNS
sudo ./simcom-cm &
sudo udhcpc -i wwan0
sudo route add -net 0.0.0.0 wwan0
```

## Update Crontab

```
crontab -e
```

```
@reboot sudo -b /home/pi/SIM8200_for_RPI/Goonline/simcom-cm -f /home/pi/SIM8200_log.txt
@reboot sudo -b udhcpc -i wwan0 -b
```

# Setup Gateway

```
cd /home/pi
mkdir /home/pi/acropolis
cd /home/pi/acropolis/
mkdir data
mkdir logs
sudo usermod -aG docker $USER
sudo reboot
```

### Copy Files

- Copy `run_dockerized_gateway.sh` to /home/pi/acropolis/
- Update `THINGSBOARD_PROVISION_*` environment parameters

```
git clone https://github.com/tum-esm/ACROPOLIS-edge.git ./acropolis-edge
sudo ./build_gateway_runner_docker_image.sh
./run_dockerized_gateway.sh
```
