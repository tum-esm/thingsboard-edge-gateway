import random
import os
import re
import time
from typing import Any, Tuple, Optional
import gpiozero
import gpiozero.pins.pigpio
import serial

from src.hardware.sensors.base_sensor import Sensor
from src.custom_types import config_types, sensor_types
from src.utils import gpio_pin_factory, list_operations

measurement_pattern = (
    pattern
) = r"Dn=([0-9.]+)D,Dm=([0-9.]+)D,Dx=([0-9.]+)D,Sn=([0-9.]+)M,Sm=([0-9.]+)M,Sx=([0-9.]+)M"
device_status_pattern = r"Th=([0-9.]+)C,Vh=([0-9.]+)N,Vs=([0-9.]+)V,Vr=([0-9.]+)V"

WXT532_SENSOR_POWER_PIN_OUT = os.environ.get("WXT532_SENSOR_POWER_PIN_OUT")
WXT532_SENSOR_SERIAL_PORT = os.environ.get("WXT532_SENSOR_SERIAL_PORT")


class VaisalaWXT532(Sensor):
    """Class for the Vaisala WXT532 sensor."""

    def __init__(self, config: config_types.Config, simulate: bool = False):
        super().__init__(config, simulate=simulate)

        self.buffered_messages: list[str] = []
        self.latest_device_status: Optional[
            sensor_types.WindSensorStatus] = None

    def _initialize_sensor(self) -> None:
        """Initialize the sensor."""
        self.pin_factory = gpio_pin_factory.get_gpio_pin_factory()
        self.power_pin = gpiozero.OutputDevice(pin=WXT532_SENSOR_POWER_PIN_OUT,
                                               pin_factory=self.pin_factory)
        self.power_pin.on()

        self.wxt532_interface = serial.Serial(
            port=WXT532_SENSOR_SERIAL_PORT,
            baudrate=19200,
            bytesize=8,
            parity="N",
            stopbits=1,
        )

        self.current_input_stream = ""

    def _shutdown_sensor(self) -> None:
        """Shutdown the sensor."""
        self.power_pin.off()
        self.pin_factory.close()

    def _read(
        self, *args: Any, **kwargs: Any
    ) -> Tuple[
            Optional[sensor_types.WindSensorData],
            Optional[sensor_types.WindSensorStatus],
    ]:
        """Read the sensor value."""
        # Update all buffered messages
        self.read_messages_in_buffer()
        # Differentiate between measurement and device status messages
        wind_measurements = self._split_wind_sensor_messages()
        # aggregate the latest measurements
        wind_measurement = self._aggregate_sensor_messages(wind_measurements)

        return (wind_measurement, self.latest_device_status)

    def _simulate(
        self
    ) -> Tuple[
            Optional[sensor_types.WindSensorData],
            Optional[sensor_types.WindSensorStatus],
    ]:
        """Simulate the sensor value."""
        return sensor_types.WindSensorData(
            speed_avg=round(random.uniform(0, 20), 2),
            speed_max=round(random.uniform(0, 20), 2),
            speed_min=round(random.uniform(0, 20), 2),
            direction_avg=round(random.uniform(0, 360), 2),
            direction_max=round(random.uniform(0, 360), 2),
            direction_min=round(random.uniform(0, 360), 2),
            last_update_time=round(
                time.time())), sensor_types.WindSensorStatus(
                    temperature=round(random.uniform(-20, 60), 2),
                    heating_voltage=round(random.uniform(0, 24), 2),
                    supply_voltage=round(random.uniform(0, 24), 2),
                    reference_voltage=round(random.uniform(0, 5), 2),
                    last_update_time=round(time.time()),
                )

    def read_messages_in_buffer(self) -> None:
        """Read the raw output from the sensor."""
        new_input_bytes = self.wxt532_interface.read_all()
        if new_input_bytes is None:
            return

        self.current_input_stream += new_input_bytes.decode("cp1252")
        messages = self.current_input_stream.split("\r\n")
        # Keep the last message in the buffer to ensure that all messages are complete
        self.current_input_stream = messages[-1]
        # Add all messages except the last one to the buffer
        self.buffered_messages += messages[:-1]

    def _split_wind_sensor_messages(self) -> list[sensor_types.WindSensorData]:
        """Split the wind sensor messages into measurement and device status messages."""

        wind_measurements: list[sensor_types.WindSensorData] = []

        for message in self.buffered_messages:
            # Check if there's a match for the measurement_pattern
            measurement_match = re.search(measurement_pattern, message)
            if measurement_match is not None:
                # Extract the values using group() method
                measurement_message = sensor_types.WindSensorData(
                    direction_min=measurement_match.group(1),
                    direction_avg=measurement_match.group(2),
                    direction_max=measurement_match.group(3),
                    speed_min=measurement_match.group(4),
                    speed_avg=measurement_match.group(5),
                    speed_max=measurement_match.group(6),
                    last_update_time=round(time.time()),
                )
                wind_measurements.append(measurement_message)

            # Check if there's a match for the device_status_pattern
            device_match = re.search(device_status_pattern, message)
            if device_match is not None:
                # Extract the values using group() method
                self.latest_device_status = sensor_types.WindSensorStatus(
                    temperature=device_match.group(1),
                    heating_voltage=device_match.group(2),
                    supply_voltage=device_match.group(3),
                    reference_voltage=device_match.group(4),
                    last_update_time=round(time.time()),
                )

        self.buffered_messages = []
        return (wind_measurements)

    def _aggregate_sensor_messages(
        self, wind_measurements: list[sensor_types.WindSensorData]
    ) -> Optional[sensor_types.WindSensorData]:

        # Aggregate the latest measurements
        if len(wind_measurements) > 0:
            self.logger.info(
                f"Processed {len(wind_measurements)} wind sensor measurements during the last "
                f"{self.config.measurement.procedure_seconds} seconds interval."
            )

            return sensor_types.WindSensorData(
                direction_min=min([m.direction_min
                                   for m in wind_measurements]),
                direction_avg=list_operations.avg_list(
                    [m.direction_avg for m in wind_measurements], 1),
                direction_max=max([m.direction_max
                                   for m in wind_measurements]),
                speed_min=min([m.speed_min for m in wind_measurements]),
                speed_avg=list_operations.avg_list(
                    [m.speed_avg for m in wind_measurements], 1),
                speed_max=max([m.speed_max for m in wind_measurements]),
                last_update_time=[
                    m.last_update_time for m in wind_measurements
                ][-1],
            )
        else:
            return None

    def check_errors(self) -> None:
        if self.simulate:
            self.logger.info("No errors detected in simulation mode.")
            return

        if self.latest_device_status is None:
            self.logger.info("No device status available.")
            return

        now = time.time()

        if (now - self.latest_device_status.last_update_time) > 300:
            self.logger.info("Device status is older than 5 minutes.")
            return

        assert (22 <= self.latest_device_status.heating_voltage <= 26)
        assert (22 <= self.latest_device_status.supply_voltage <= 26)
        assert (3.2 <= self.latest_device_status.reference_voltage <= 4.0)

        self.logger.info("The wind sensor check doesn't report any errors")
