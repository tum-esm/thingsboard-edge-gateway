# Raspberry Pi 4 Edge Client Setup

This guide provides step-by-step instructions to set up a Raspberry Pi 4 as an edge client for the Acropolis project. It includes OS installation, dependency setup, modem configuration, and running the gateway.

## File Structure

```bash
📁 RPi-edge-client
    📄 config.txt
    📄 default.script
    📄 README.md
```

## 1. Install Raspberry Pi OS

- Download and install **Raspberry Pi OS Lite (64-bit)**.
- Configure **SSH, WiFi, and Hostname**.
- Copy `config.txt` into the `bootfs` folder on the SD card.

## 2. Install Dependencies

Update the package list and install required dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    build-essential libssl-dev libbz2-dev \
    libexpat1-dev liblzma-dev zlib1g-dev \
    libffi-dev openssl docker.io git \
    tldr ncdu minicom pigpio libsqlite3-dev \
    wget screen udhcpc
```

Enable **I2C Interface** using:

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## 3. Set Up Docker

Create a Docker daemon configuration file:

```bash
sudo nano /etc/docker/daemon.json
# Add:
{
    "dns": ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
}
```

Add the current user to the Docker group and reboot:

```bash
sudo usermod -aG docker $USER
sudo reboot
```

## 4. Install Python 3.12

```bash
wget https://www.python.org/ftp/python/3.12.8/Python-3.12.8.tgz
sudo tar zxf Python-3.12.8.tgz
cd Python-3.12.8
sudo ./configure --enable-optimizations --enable-loadable-sqlite-extensions
sudo make -j 4
sudo make install
curl -sSL https://install.python-poetry.org/ | python3.12 -
```

## 5. Configure Modem

### **AT Commands for Modem Setup**

```bash
sudo minicom -D /dev/ttyS0
# Check modem functionality
AT
# Enable terminal echo
ATE1
# Switch modem to RNDIS mode
AT+CUSBPIDSWITCH=9001,1,1
# Set SIM APN
AT+CGDCONT=1,"IP","iotde.telefonica.com"
# Enable automatic network registration
AT+COPS=0
# Set LTE only mode
AT+CNMP=38
```

### **Install SIM8200 Modem Driver**

```bash
cd /home/pi
wget https://www.waveshare.net/w/upload/8/89/SIM8200_for_RPI.7z
7z x SIM8200_for_RPI.7z -r -o./SIM8200_for_RPI
sudo chmod 777 -R SIM8200_for_RPI
cd SIM8200_for_RPI/Goonline
make clean && make
```

## 6. Set Up Networking & System Automation

### **Install and Configure UDHCPC**

```bash
cd /home/pi/acropolis/setup/RPi-edge-client
sudo cp default.script /usr/share/udhcpc/
sudo chmod -R 0777 /usr/share/udhcpc/
```

### **Create acropolis folder**

```bash
sudo mkdir -p /home/pi/acropolis/
git clone https://github.com/tum-esm/ACROPOLIS-edge.git ./acropolis-edge
sudo git config --system --add safe.directory '*'
cd /home/pi/acropolis/setup/RPi-edge-client
sudo cp network_lost_reboot_trigger.sh /home/pi/acropolis/
sudo chmod a+x /home/pi/acropolis/network_lost_reboot_trigger.sh
sudo cp run_dockerized_gateway.sh /home/pi/acropolis/
sudo chmod a+x /home/pi/acropolis/run_dockerized_gateway.sh
```

### **Update Crontab for Automation**

Edit crontab:

```bash
sudo crontab -e
```

Add:

```
# Add binary folders to PATH
PATH=/usr/sbin:/usr/bin:/sbin:/bin

# GSM Modem
@reboot sleep 10 && sudo -b /home/pi/SIM8200_for_RPI/Goonline/simcom-cm
@reboot sudo -b udhcpc -i wwan0 -b

# GPIO-Pins
@reboot /usr/bin/pigpiod -n 127.0.0.1

# Docker
@daily docker system prune -a --force --filter "until=8760h"

# Reboot on connectivity loss
@daily /bin/bash /home/pi/acropolis/network_lost_reboot_trigger.sh

# Delete old log files (older than 100 days)
@daily /usr/bin/find /home/pi/acropolis/logs/ -type f -mtime +100 -delete
```

# Setup Gateway

```bash
cd /home/pi
mkdir -p /home/pi/acropolis/data
mkdir -p /home/pi/acropolis/logs
```

### **Clone and Build Gateway**

```bash
cd /home/pi/acropolis/software/gateway
sudo ./build_gateway_runner_docker_image.sh
# Update `THINGSBOARD_PROVISION_*` environment parameters in file: run_dockerized_gateway.sh
```

(Optional) Skip if you want to create an template image for multiple systems

```bash
./run_dockerized_gateway.sh #registers device with ThingsBoard and creates tb_access_token
docker logs --tail 50 -f acropolis_edge_gateway
```

## 8. Create & Flash SD Card Image

Remove SD Card and insert into personal computer

### **Create Backup Image**

```bash
diskutil list
diskutil umountDisk /dev/disk[*]
dd status=progress bs=4M  if=/dev/disk[*] | gzip > //Users/.../acropolis-edge-image.gz
```

## 9. Fast Setup for additional systems

Insert fresh SD Card into personal computer

### **Flash Image to SD Card**

```bash
diskutil list
diskutil umountDisk /dev/disk[*]
gzip -dc //Users/.../acropolis-edge-image.gz | sudo dd of=/dev/disk[*] bs=4M status=progres
```

Remove SD Card and insert into RaspberryPi

### **Change Hostname**

```bash
sudo raspi-config
# Navigate to: System Options → Hostname
reboot
```

### **Run Gateway Script**

```bash
cd /home/pi/acopolis/acropolis-edge/software/gateway
# make sure no 'tb_access_token' exists
cd /home/pi/acopolis
./run_dockerized_gateway.sh
docker logs --tail 50 -f acropolis_edge_gateway
```

---

This completes the setup for the Raspberry Pi 4 Edge Client.
