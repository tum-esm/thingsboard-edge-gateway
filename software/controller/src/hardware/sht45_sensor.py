import random
import time
import adafruit_sht4x
try:
    import board
    import busio
except:
    pass

from custom_types import config_types, sensor_types
from interfaces import logging_interface


class SHT45SensorInterface:

    def __init__(
        self,
        config: config_types.Config,
        testing: bool = False,
        simulate: bool = False,
    ) -> None:
        self.logger = logging_interface.Logger(config=config,
                                               origin="sht45-sensor")
        self.config = config
        self.simulate = simulate
        self.logger.info("Starting initialization.")

        if self.simulate:
            self.sensor_connected = True
            self.logger.info("Simulating SHT45 sensor.")
            return

        # set up connection to SHT45 sensor
        self.sensor_connected = False
        for _ in range(2):
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.sht = adafruit_sht4x.SHT4x(self.i2c)
                self.logger.debug(
                    f"Found SHT4x with serial number {hex(self.sht.serial_number)}"
                )
                self.sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
                # sensor didn't raise any issue during connection
                self.sensor_connected = True
                break
            except Exception as e:
                self.logger.exception(
                    e,
                    label="Could not initialize SHT45 sensor",
                    forward=True,
                )

            time.sleep(1)

        if not self.sensor_connected:
            self.logger.warning(
                "Could not connect to SHT45 sensor.",
                forward=True,
            )

        self.logger.info("finished initialization.")

    def get_data(self, retries: int = 1) -> sensor_types.SHT45SensorData:
        """Reads temperature and humidity in the air inlet"""

        if self.simulate:
            return sensor_types.SHT45SensorData(
                temperature=round(5.0 + 25.0 * random.random(), 2),
                humidity=round(10.0 + 85.0 * random.random(), 2),
            )

        # initialize output
        output = sensor_types.SHT45SensorData(
            temperature=None,
            humidity=None,
        )

        # returns None if no air-inlet sensor is connected
        if not self.sensor_connected:
            self.logger.warning(
                "Did not fetch SHT45 sensor data. Device is not connected.", )
            return output

        # read sht45 data (retries one time)
        for _ in range(retries + 1):
            try:
                temperature, relative_humidity = self.sht.measurements
                output.temperature = round(temperature, 2)
                output.humidity = round(relative_humidity, 2)
                return output

            except Exception:
                self.logger.warning(
                    "Problem during sensor readout. Reinitialising sensor communication",
                    forward=True,
                )
                self._reset_sensor()

        # returns None if sensor could not be read
        self.logger.warning(
            "Could not read SHT45 measurement values. Device is not connected.",
            forward=True,
        )
        return output

    def _reset_sensor(self) -> None:
        try:
            self.sht.reset()
            self.sensor_connected = True
            time.sleep(1)
        except Exception:
            self.logger.warning(f"Reset of the SHT45 sensor failed.", )
            self.sensor_connected = False
