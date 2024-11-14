import gpiozero
from .get_gpio_pin_factory import get_gpio_pin_factory


# initialize interface
pin_factory = get_gpio_pin_factory()
pin = gpiozero.OutputDevice(26, pin_factory=pin_factory)

def set_venitlation_on():
    pin.on()
    
def set_venitlation_off():
    pin.off()
    
