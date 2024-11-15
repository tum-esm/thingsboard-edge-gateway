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


# Define the simulated system (the plant)
class HeaterSystem:

    def __init__(self):
        self.temperature = read_sensor_temperature()

    def update(self, control_signal):
        """Update the PWM duty cycle based on the temperature."""
        HC.set_heater_pwm(control_signal)
        self.temperature = read_sensor_temperature()
        return self.temperature


# Initialize components
VC = VentilationControl()
HC = HeaterControl()
system = HeaterSystem()
pid = PID(1, 0.1, 0.05, setpoint=40)
pid.output_limits = (0, 1)

# Activate ventilation at the start
VC.set_venitlation_on()
logging.info(
    f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')}: Ventilation started"
)


# Set up signal handling for safe shutdown
def shutdown_handler(signal, frame):
    """Handle program exit safely by shutting down heater and ventilation."""
    logging.info(
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')}: Shutting down..."
    )
    HC.set_heater_pwm(0)
    VC.set_venitlation_off()
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

try:
    # Set initial values and logging interval
    temp = system.update(0)
    print_frequency = time.time()

    while True:
        try:
            # Calculate control output and update system state
            control = pid(temp)
            temp = system.update(control)

            # Check if logging interval has passed
            if time.time() - print_frequency > 5:
                logging.info(
                    f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')}: "
                    f"Temperature: {round(system.temperature, 2)}, Control: {round(control, 2)}"
                )
                print_frequency = time.time()

            # Control loop sleep
            time.sleep(0.1)

        except Exception as e:
            logging.error(
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')}: Error - {e}"
            )
            # Reinitialize interfaces to ensure that GPIO pins are available
            VC = VentilationControl()
            HC = HeaterControl()

finally:
    # Final cleanup in case of an unexpected exit
    HC.set_heater_pwm(0)
    VC.set_venitlation_off()
    logging.info(
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')}: Heater and ventilation powered off."
    )
