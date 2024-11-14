import gpiozero

def get_gpio_pin_factory() -> gpiozero.pins.pigpio.PiGPIOFactory:
    """
    Connects to the active pipiod deamon running on the Pi over network socket.
    Documentation: https://gpiozero.readthedocs.io/en/latest/api_pins.html#gpiozero.pins.pigpio.PiGPIOFactory
    """

    try:
        pin_factory = gpiozero.pins.pigpio.PiGPIOFactory(host="127.0.0.1")
        assert pin_factory.connection is not None
        assert pin_factory.connection.connected
    except:
        raise ConnectionError(
            'pigpio is not connected, please run "sudo pigpiod -n 127.0.0.1"'
        )
    return pin_factory