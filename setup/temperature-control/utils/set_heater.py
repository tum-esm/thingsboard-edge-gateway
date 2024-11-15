import time
import gpiozero
import logging
from .gpio_helper import get_gpio_pin_factory

logger = logging.getLogger(__name__)

class HeaterControl:
    def __init__(self):
        """Initialize GPIO interface for the heater."""
        self.pin = None
        self.pin_factory = None
        self.initialize_interface()

    def initialize_interface(self, retries=3, delay=2):
        """
        (Re)initialize the GPIO interface, with retries on failure.

        Args:
            retries (int): Number of retries for initialization.
            delay (int): Delay (seconds) between retries.
        """
        for attempt in range(retries):
            try:
                self.pin_factory = get_gpio_pin_factory()
                self.pin = gpiozero.PWMOutputDevice(
                    pin=18,
                    active_high=True,
                    initial_value=0,
                    frequency=10000,
                    pin_factory=self.pin_factory,
                )
                logger.info("Heater interface initialized successfully.")
                return
            except (gpiozero.BadPinFactory, RuntimeError) as e:
                logger.warning(f"GPIO initialization failed: {e} (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)

        # If all retries fail, raise an exception
        raise RuntimeError("Failed to initialize GPIO interface for heater after multiple attempts.")

    def ensure_interface_available(self):
        """Ensure the GPIO interface is available and healthy."""
        if self.pin is None or self.pin_factory is None or not self.pin_factory.pins:
            logger.info("GPIO interface unavailable for heater. Reinitializing...")
            self.initialize_interface()

    def set_heater_pwm(self, pwm_duty_cycle=0):
        """
        Set the PWM duty cycle for the heater.

        Args:
            pwm_duty_cycle (float): A value between 0 and 1 representing the duty cycle.

        Raises:
            AssertionError: If the duty cycle is outside the valid range.
            RuntimeError: If the GPIO operation fails.
        """
        assert 0 <= pwm_duty_cycle <= 1, f"PWM duty cycle must be between 0 and 1 (passed {pwm_duty_cycle})"

        self.ensure_interface_available()
        try:
            self.pin.value = pwm_duty_cycle
        except Exception as e:
            logger.error(f"Failed to set heater PWM: {e}")
            raise RuntimeError("Heater control error: Unable to set PWM.")