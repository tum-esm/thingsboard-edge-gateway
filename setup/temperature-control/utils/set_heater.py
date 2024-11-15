import gpiozero
from .get_gpio_pin_factory import get_gpio_pin_factory


class HeaterControl():

    def __init__(self):
        # initialize interface
        self.pin = gpiozero.PWMOutputDevice(
            pin=18,
            active_high=True,
            initial_value=0,
            frequency=10000,
            pin_factory=get_gpio_pin_factory(),
        )

    def set_heater_pwm(self, pwm_duty_cycle=0):
        assert (
            0 <= pwm_duty_cycle <= 1
        ), f"pwm duty cycle has to be between 0 and 1 (passed {pwm_duty_cycle})"

        self.pin.value = pwm_duty_cycle
