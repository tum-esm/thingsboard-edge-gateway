import time
from datetime import datetime, timezone
try:
    from simple_pid import PID
except Exception:
    pass

from custom_types import config_types
from interfaces import logging_interface
from utils import message_queue
from hardware.sensors.grove_MCP9808 import GroveMCP9808
from hardware.actuator.heat_box_heater import HeatBoxHeater
from hardware.actuator.heat_box_ventilator import HeatBoxVentilator

# TODO: Run as thread


class HeatingBoxModule:
    """Combines sensor and actor interfaces."""

    def __init__(self, config: config_types.Config,
                 temperature_sensor: GroveMCP9808, heater: HeatBoxHeater,
                 ventilator: HeatBoxVentilator) -> None:

        self.logger = logging_interface.Logger(config=config,
                                               origin="CO2MeasurementModule")
        self.config = config
        self.message_queue = message_queue.MessageQueue()

        # hardware
        self.temperature_sensor = temperature_sensor
        self.heater = heater
        self.ventilator = ventilator

        # pid
        self.pid = PID(1, 0.1, 0.05, setpoint=40)
        self.pid.output_limits = (0, 1)

        # default actor values
        self.heater.set(pwm_duty_cycle=0)
        self.ventilator.start()

    def run(self) -> None:
        """Runs the PID to control for temperature."""

        try:
            last_log_timestamp = 0.0

            while True:
                # Calculate control output and update system state
                temp = self.temperature_sensor.read_with_retry()  #ignoreType
                assert isinstance(
                    temp, float
                ), "Temperature should be a float after the None check."

                control = self.pid(temp)

                self.heater.set(pwm_duty_cycle=control)

                # Check if logging interval has passed
                if time.time() - last_log_timestamp > 5:
                    self.logger.info(
                        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}: "
                        f"Temperature: {round(temp, 2)}, Control: {round(control, 2)}"  # type: ignore[arg-type]
                    )
                    last_log_timestamp = time.time()

                # Control loop sleep
                time.sleep(0.1)
        except Exception as e:
            self.logger.error(
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}: Error - {e}"
            )
        finally:
            # Final cleanup in case of an unexpected exit
            self.teardown()
            self.logger.info(
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}: Heater and ventilation powered off."
            )

    def teardown(self) -> None:
        """set default actor values"""
        self.heater.set(pwm_duty_cycle=0)
        self.ventilator.stop()
