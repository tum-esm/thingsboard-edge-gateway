import gpiozero
from .get_gpio_pin_factory import get_gpio_pin_factory


class VentilationControl():

    def __init__(self):
        # initialize interface
        self.pin = gpiozero.OutputDevice(26,
                                         pin_factory=get_gpio_pin_factory())

    def set_venitlation_on(self):
        self.pin.on()

    def set_venitlation_off(self):
        self.pin.off()
