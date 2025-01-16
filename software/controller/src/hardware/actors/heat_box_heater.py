from typing import Any

try:
    import gpiozero
except Exception:
    pass

from hardware.actors import base_actor
from custom_types import config_types


class HeatBoxHeater(base_actor.Actor):
    """Class for controlling the heat box heater."""

    def __init__(self,
                 config: config_types.Config,
                 pin_factory: gpiozero.pins.pigpio.PiGPIOFactory,
                 max_retries: int = 3,
                 retry_delay: float = 0.5):

        super().__init__(config=config,
                         max_retries=max_retries,
                         retry_delay=retry_delay,
                         pin_factory=pin_factory)

    def _initialize_actor(self) -> None:
        """Initializes the heat box heater."""

        self.power_pin = gpiozero.PWMOutputDevice(
            pin=self.config.hardware.heat_box_heater_power_pin_out,
            active_high=True,
            initial_value=0,
            frequency=self.config.hardware.heat_box_heater_power_pin_frequency,
            pin_factory=self.pin_factory,
        )

    def _shutdown_actor(self) -> None:
        """Shuts down the heat box heater."""

        if hasattr(
                self,
                "power_pin") and self.power_pin and not self.power_pin.closed:
            self.power_pin.off()
            # Shut down the device and release all associated resources (such as GPIO pins).
            self.power_pin.close()
        else:
            self.logger.warning(
                "Power pin is uninitialized or already closed.")

    def _set(self, *args: Any, **kwargs: float) -> None:
        """Sets the PWM signal for the heat box heater."""

        pwm_duty_cycle = kwargs.get('pwm_duty_cycle', 0)

        assert (
            0 <= pwm_duty_cycle <= 1
        ), f"pwm duty cycle has to be between 0 and 1 (passed {pwm_duty_cycle})"
        self.power_pin.value = pwm_duty_cycle
