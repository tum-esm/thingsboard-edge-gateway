## Installation

**Set up virtual environment and install dependencies:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
poetry install --with=dev
```

**Set GPIO pins**

```bash
sudo nano /boot/firmware/config.txt

# PWM Settings
dtoverlay=pwm,pin=18,func=5

# Heat Box Ventilator Power
gpio=26=op=dl
```
