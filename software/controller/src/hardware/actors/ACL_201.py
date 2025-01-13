import time
from typing import Literal
import gpiozero

from hardware.actors import base_actor
from custom_types import config_types

VALVE_PIN_1_OUT = 25
VALVE_PIN_2_OUT = 24
VALVE_PIN_3_OUT = 23
VALVE_PIN_4_OUT = 22


class ACLValves(base_actor.Actor):
    """Class for controlling the SP 622 EC_BL membrane pump."""

    def __init__(self,
                 config: config_types.Config,
                 pin_factory: gpiozero.pins.pigpio.PiGPIOFactory,
                 simulate=False,
                 max_retries=3,
                 retry_delay=0.5):
        super().__init__(config=config,
                         simulate=simulate,
                         max_retries=max_retries,
                         retry_delay=retry_delay,
                         pin_factory=pin_factory)

        self.default_pwm_duty_cycle = config.hardware.pump_pwm_duty_cycle

    def _initialize_actor(self):
        """Initializes the membrane pump."""

        # initialize device and reserve GPIO pin
        self.valves: dict[Literal[1, 2, 3, 4], gpiozero.OutputDevice] = {
            1:
            gpiozero.OutputDevice(VALVE_PIN_1_OUT,
                                  pin_factory=self.pin_factory),
            2:
            gpiozero.OutputDevice(VALVE_PIN_2_OUT,
                                  pin_factory=self.pin_factory),
            3:
            gpiozero.OutputDevice(VALVE_PIN_3_OUT,
                                  pin_factory=self.pin_factory),
            4:
            gpiozero.OutputDevice(VALVE_PIN_4_OUT,
                                  pin_factory=self.pin_factory),
        }
        self.active_input: Literal[1, 2, 3,
                                   4] = self.config.measurement.valve_number

    def _shutdown_actor(self):
        """Shuts down the membrane pump."""

        self.control_pin.off()
        # Shut down the device and release all associated resources (such as GPIO pins).
        self.control_pin.close()

    def _set(self, *args, **kwargs):
        pwm_duty_cycle = kwargs.get('pwm_duty_cycle',
                                    self.default_pwm_duty_cycle)

        assert (
            0 <= pwm_duty_cycle <= 1
        ), f"pwm duty cycle has to be between 0 and 1 (passed {pwm_duty_cycle})"
        self.control_pin.value = pwm_duty_cycle

    def flush_system(self, duration: int, pwm_duty_cycle: float):
        """Flushes the system with the pump for a given duration and duty cycle."""
        assert (
            0 <= pwm_duty_cycle <= 1
        ), f"pwm duty cycle has to be between 0 and 1 (passed {pwm_duty_cycle})"

        self.set(pwm_duty_cycle=pwm_duty_cycle)
        time.sleep(duration)
        self.set(pwm_duty_cycle=self.default_pwm_duty_cycle)
