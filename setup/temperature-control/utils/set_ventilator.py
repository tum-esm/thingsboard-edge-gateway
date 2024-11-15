import time
from gpiozero import OutputDevice, BadPinFactory
from .gpio_helper import get_gpio_pin_factory
import logging

logger = logging.getLogger(__name__)

class VentilationControl:
    def __init__(self):
        """Initialize GPIO interface with health checks."""
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
                self.pin = OutputDevice(26, pin_factory=self.pin_factory)
                logger.info("Ventilation interface initialized successfully.")
                return
            except (BadPinFactory, RuntimeError) as e:
                logger.warning(f"GPIO initialization failed: {e}")
                time.sleep(delay)

        # If all retries fail, raise an exception
        raise RuntimeError("Failed to initialize GPIO interface after multiple attempts.")

    def ensure_interface_available(self):
        """Ensure the GPIO interface is available and healthy."""
        if self.pin is None or self.pin_factory is None or not self.pin_factory.pins:
            logger.info("GPIO interface unavailable. Reinitializing...")
            self.initialize_interface()

    def set_ventilation_on(self):
        """Turn ventilation on."""
        self.ensure_interface_available()
        try:
            self.pin.on()
            logger.info("Ventilation turned on.")
        except Exception as e:
            logger.error(f"Failed to turn ventilation on: {e}")
            raise RuntimeError("Ventilation control error: Unable to turn on.")

    def set_ventilation_off(self):
        """Turn ventilation off."""
        self.ensure_interface_available()
        try:
            self.pin.off()
            logger.info("Ventilation turned off.")
        except Exception as e:
            logger.error(f"Failed to turn ventilation off: {e}")
            raise RuntimeError("Ventilation control error: Unable to turn off.")