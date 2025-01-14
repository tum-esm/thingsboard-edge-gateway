import time
from typing import Any
try:
    import gpiozero
    import gpiozero.pins.pigpio
except Exception:
    pass

from hardware.actors import base_actor
from custom_types import config_types

PUMP_CONTROL_PIN_OUT = 19
PUMP_CONTROL_PIN_FREQUENCY = 10000
PUMP_SPEED_PIN_IN = 16


class SchwarzerPrecisionPump(base_actor.Actor):
    """Class for controlling the SP 622 EC_BL membrane pump."""

    def __init__(
        self,
        config: config_types.Config,
        pin_factory: gpiozero.pins.pigpio.PiGPIOFactory,
        simulate: bool = False,
        max_retries: int = 3,
        retry_delay: float = 0.5,
    ):
        super().__init__(config=config,
                         simulate=simulate,
                         max_retries=max_retries,
                         retry_delay=retry_delay)

        self.pin_factory = pin_factory
        self.default_pwm_duty_cycle = config.hardware.pump_pwm_duty_cycle

    def _initialize_actor(self) -> None:
        """Initializes the membrane pump."""

        # initialize device and reserve GPIO pin
        self.control_pin = gpiozero.PWMOutputDevice(
            pin=PUMP_CONTROL_PIN_OUT,
            active_high=True,
            initial_value=False,
            frequency=PUMP_CONTROL_PIN_FREQUENCY,
            pin_factory=self.pin_factory,
        )

        # start pump to run continuously
        self.set(pwm_duty_cycle=self.default_pwm_duty_cycle)

    def _shutdown_actor(self) -> None:
        """Shuts down the membrane pump."""

        self.control_pin.off()
        # Shut down the device and release all associated resources (such as GPIO pins).
        self.control_pin.close()

    def _set(self, *args: Any, **kwargs: float) -> None:
        pwm_duty_cycle = kwargs.get('pwm_duty_cycle',
                                    self.default_pwm_duty_cycle)

        assert (
            0 <= pwm_duty_cycle <= 1
        ), f"pwm duty cycle has to be between 0 and 1 (passed {pwm_duty_cycle})"
        self.control_pin.value = pwm_duty_cycle

    def flush_system(self, duration: int, pwm_duty_cycle: float) -> None:
        """Flushes the system with the pump for a given duration and duty cycle."""
        assert (
            0 <= pwm_duty_cycle <= 1
        ), f"pwm duty cycle has to be between 0 and 1 (passed {pwm_duty_cycle})"

        self.set(pwm_duty_cycle=pwm_duty_cycle)
        time.sleep(duration)
        self.set(pwm_duty_cycle=self.default_pwm_duty_cycle)
