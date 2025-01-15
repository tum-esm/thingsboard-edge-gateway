import time
from typing import Optional, Literal

from custom_types import config_types, sensor_types
from custom_types import mqtt_playload_types
from interfaces import hardware_interface, logging_interface
from utils import message_queue, ring_buffer


class CO2MeasurementModule:
    """Combines sensor and actor interfaces."""

    def __init__(
            self, config: config_types.Config,
            hardware_interface: hardware_interface.HardwareInterface) -> None:

        self.logger, self.config = logging_interface.Logger(
            config=config, origin="measurement-procedure"), config
        self.hardware_interface = hardware_interface

        # state variables
        self.active_air_inlet: Optional[Literal[1, 2, 3, 4]] = None
        self.last_measurement_time: float = 0
        self.message_queue = message_queue.MessageQueue()
        self.rb_pressure = ring_buffer.RingBuffer(
            self.config.measurement.average_air_inlet_measurements)
        self.rb_humidity = ring_buffer.RingBuffer(
            self.config.measurement.average_air_inlet_measurements)

    def run_CO2_measurement_interval(self) -> None:
        """do regular measurements for in config defined measurement interval"""

        measurement_procedure_start_time = time.time()
        while True:
            # idle until next measurement period
            seconds_to_wait_for_next_measurement = max(
                self.config.hardware.gmp343_filter_seconds_averaging -
                (time.time() - self.last_measurement_time),
                0,
            )
            self.logger.debug(
                f"sleeping {round(seconds_to_wait_for_next_measurement, 3)} seconds"
            )
            time.sleep(seconds_to_wait_for_next_measurement)
            self.last_measurement_time = time.time()

            # Get latest auxiliary sensor data information
            self._update_air_inlet_parameters()

            # perform a CO2 measurement
            CO2_sensor_data = (
                self.hardware_interface.co2_sensor.read_with_retry(
                    pressure=self.rb_pressure.avg(),
                    humidity=self.rb_humidity.avg(),
                ))
            self.logger.debug(f"new measurement: {CO2_sensor_data}")

            self._send_CO2_sensor_data(CO2_sensor_data=CO2_sensor_data)

            # stop loop after defined measurement interval
            if (self.last_measurement_time - measurement_procedure_start_time
                ) >= self.config.measurement.procedure_seconds:
                break

    def _update_air_inlet_parameters(self) -> None:
        """
        fetches the latest temperature and pressure data at air inlet
        """

        self.air_inlet_bme280_data = (
            self.hardware_interface.air_inlet_bme280_sensor.read_with_retry())

        # Add to ring buffer to calculate moving average of low-cost sensor
        self.rb_pressure.append(self.air_inlet_bme280_data.pressure)

        self.air_inlet_sht45_data = (
            self.hardware_interface.air_inlet_sht45_sensor.read_with_retry())

        # Add to ring buffer to calculate moving average of low-cost sensor
        self.rb_humidity.append(self.air_inlet_sht45_data.humidity)

    def _send_CO2_sensor_data(
            self, CO2_sensor_data: sensor_types.CO2SensorData) -> None:
        # send out MQTT measurement message
        self.message_queue.enqueue_message(
            timestamp=int(time.time()),
            payload=mqtt_playload_types.MQTTCO2Data(
                gmp343_raw=CO2_sensor_data.raw,
                gmp343_compensated=CO2_sensor_data.compensated,
                gmp343_filtered=CO2_sensor_data.filtered,
                gmp343_temperature=CO2_sensor_data.temperature,
                bme280_temperature=self.air_inlet_bme280_data.temperature,
                bme280_humidity=self.air_inlet_bme280_data.humidity,
                bme280_pressure=self.air_inlet_bme280_data.pressure,
                sht45_temperature=self.air_inlet_sht45_data.temperature,
                sht45_humidity=self.air_inlet_sht45_data.humidity,
            ),
        )
