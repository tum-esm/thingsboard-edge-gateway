import random
from typing import Any
try:
    import adafruit_sht4x
    import board
    import busio
except:
    pass

from hardware.sensors._base_sensor import Sensor
from custom_types import config_types, sensor_types
from interfaces import state_interface


class SensirionSHT45(Sensor):
    """Class for the Sensirion SHT45 sensor."""

    def __init__(self, config: config_types.Config):
        super().__init__(config=config)

        state = state_interface.StateInterface.read(config=self.config)
        self.sht.humidity_offset = state.sht45_humidity_offset

    def _initialize_sensor(self) -> None:
        """Initialize the sensor."""
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sht = adafruit_sht4x.SHT4x(self.i2c)
        self.logger.debug(
            f"Found SHT4x with serial number {hex(self.sht.serial_number)}")
        self.sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

    def _shutdown_sensor(self) -> None:
        """Shutdown the sensor."""
        self.sht.reset()

    def _read(self, *args: Any, **kwargs: Any) -> sensor_types.SHT45SensorData:
        """Read the sensor value."""
        temperature, relative_humidity = self.sht.measurements

        return sensor_types.SHT45SensorData(
            temperature=temperature,
            humidity=relative_humidity,
        )

    def _simulate_read(self, *args: Any,
                       **kwargs: Any) -> sensor_types.SHT45SensorData:
        """Simulate reading the sensor value."""
        return sensor_types.SHT45SensorData(
            temperature=random.uniform(20, 25),
            humidity=random.uniform(40, 60),
        )

    def set_humidity_offset(self, rh_offset: float) -> None:
        """Set the humidity offset."""
        self.sht.humidity_offset = rh_offset
        self.logger.debug(f"Set humidity offset to {rh_offset}.")
