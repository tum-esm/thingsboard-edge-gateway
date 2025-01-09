import time
import bme280
import smbus2
import random
from typing import Literal, Optional, Any

from src.hardware.sensors.base_sensor import Sensor
from src.custom_types import sensor_types, config_types
from src.interfaces import logging_interface


class BoschBME280(Sensor):
    """Class for the Bosch BME280 sensor."""

    def __init__(self,
                 config: config_types.Config,
                 variant: Literal["ioboard", "air-inlet"],
                 testing: bool = False,
                 simulate: bool = False):
        super().__init__(config, testing=testing, simulate=simulate)

        self.variant = variant
        self.compensation_params: Optional[bme280.params] = None

        # overwrite logger for variant
        self.logger = logging_interface.Logger(
            f"{self.__class__.__name__}:" + self.variant,
            print_to_console=testing,
            write_to_file=(not testing),
        )

    def _initialize_sensor(self) -> None:
        """Initialize the sensor."""

        self._connect_sensor()
        self._read_compensation_param()

    def _shutdown_sensor(self) -> None:
        """Shutdown the sensor."""
        self.compensation_params = None
        if self.bus:
            self.bus.close()

    def _read(self, *args: Any,
              **kwargs: Any) -> sensor_types.BME280SensorData:
        """Read the sensor value."""

        try:
            data = bme280.sample(self.bus, self.address,
                                 self.compensation_params)
            return sensor_types.BME280SensorData(
                temperature=round(data.temperature, 2),
                pressure=round(data.pressure, 2),
                humidity=round(data.humidity, 2),
            )
        except Exception as e:
            self.logger.exception(e,
                                  label="Could not read BME280 sensor data.")
            raise self.SensorError("Could not read BME280 sensor data.")

    def _simulate_read(self, *args: Any,
                       **kwargs: Any) -> sensor_types.BME280SensorData:
        """Simulate reading the sensor value."""
        return sensor_types.BME280SensorData(
            temperature=round(random.uniform(0, 50), 2),
            pressure=round(random.uniform(900, 1050), 2),
            humidity=round(random.uniform(0, 100), 2),
        )

    def _connect_sensor(self) -> None:
        """Connect to the sensor. Retry if connection fails."""

        self.sensor_connected = False
        for _ in range(2):
            try:
                self.bus = smbus2.SMBus(1)
                self.address = 0x77 if (self.variant == "ioboard") else 0x76

                # test if the sensor data can be read
                bme280.sample(
                    self.bus,
                    self.address,
                )

                # sensor didn't raise any issue during connection
                self.sensor_connected = True
                break
            except Exception as e:
                self.logger.exception(
                    e,
                    label=
                    f"Could not connect to BME280 sensor (variant: {self.variant})",
                    forward=True,
                )
                time.sleep(1)

    def _read_compensation_param(self) -> None:
        try:
            self.compensation_params = bme280.load_calibration_params(
                self.bus, self.address)
        except Exception:
            self.logger.warning("Could not fetch compensation params.", )
            self.compensation_params = None
