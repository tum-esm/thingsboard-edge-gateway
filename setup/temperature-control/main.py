import time
import logging
from datetime import datetime, timezone
from simple_pid import PID
import signal
import sys
import os

from utils.read_temperature import read_sensor_temperature
from utils.set_ventilator import VentilationControl
from utils.set_heater import HeaterControl

# Set up logging
base_path = os.path.dirname(os.path.abspath(__file__))

# Define the logfile path in the same directory as the script
logfile_path = os.path.join(base_path, 'log', 'temperature_control.log')

# Set up logging
logging.basicConfig(filename=logfile_path,
                    encoding='utf-8',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

logging.basicConfig(filename='temperature_control.log',
                    encoding='utf-8',
                    level=logging.DEBUG)


# Initialize components
VC = VentilationControl()
HC = HeaterControl()
pid = PID(1, 0.1, 0.05, setpoint=40)
pid.output_limits = (0, 1)

# Activate ventilation at the start
VC.set_ventilation_on()

# Set up signal handling for safe shutdown
def shutdown_handler(signal, frame):
    """Handle program exit safely by shutting down heater and ventilation."""
    logging.info(
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}: Signal received, shutting down gracefully..."
    )
    HC.set_heater_pwm(0)
    VC.set_ventilation_off()
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

try:
    # Set initial heater state to 0 (off) and read initial temperature
    HC.set_heater_pwm(0)
    last_log_timestamp = 0

    while True:
        # Calculate control output and update system state
        temp = read_sensor_temperature()
        control = pid(temp)
        HC.set_heater_pwm(control)

        # Check if logging interval has passed
        if time.time() - last_log_timestamp > 5:
            logging.info(
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}: "
                f"Temperature: {round(temp, 2)}, Control: {round(control, 2)}"
            )
            last_log_timestamp = time.time()

        # Control loop sleep
        time.sleep(0.1)

except Exception as e:
    logging.error(
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}: Error - {e}"
    )
finally:
    # Final cleanup in case of an unexpected exit
    HC.set_heater_pwm(0)
    VC.set_ventilation_off()
    logging.info(
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}: Heater and ventilation powered off."
    )
