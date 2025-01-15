import time
from typing import Optional, Literal

from custom_types import config_types, sensor_types
from custom_types import mqtt_playload_types
from interfaces import hardware_interface, logging_interface
from utils import message_queue, ring_buffer


class MeasurementProcedure:
    """runs every mainloop call after possible configuration/calibration

    1. Collect latest wind measurement
    2. Collect latest pressure and humidity inlet sensor readings
    3. Update compensation values for CO2 sensor
    4. Perform measurements for CO2 sensor
    5. Send out measurement data over MQTT"""

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

    def run(self) -> None:
        """
        1. Collect Wind Sensor Data
        2. Run CO2 sensor measurement interval
        """

        # Wind sensor data
        self._process_wind_sensor_data()

        # do regular measurements for in config defined measurement interval
        self.logger.info(
            f"starting {self.config.measurement.procedure_seconds} seconds long CO2 measurement interval"
        )
        self._run_CO2_measurement_interval()
        self.logger.info(f"finished CO2 measurement interval")

    def _run_CO2_measurement_interval(self) -> None:
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

    def _process_wind_sensor_data(self) -> None:
        # wind measurement

        wind_sensor_data, wind_sensor_status = self.hardware_interface.wind_sensor.read(
        )

        self._send_wind_sensor_data(wind_sensor_data=wind_sensor_data)
        self._send_wind_sensor_status(wind_sensor_status=wind_sensor_status)

    def _send_wind_sensor_data(
            self, wind_sensor_data: sensor_types.WindSensorData) -> None:
        # send latest wind measurement info
        if wind_sensor_data is not None:
            self.logger.info(
                f"latest wind sensor measurement: {wind_sensor_data}")

            self.message_queue.enqueue_message(
                timestamp=int(time.time()),
                payload=mqtt_playload_types.MQTTWindData(
                    wxt532_direction_min=wind_sensor_data.direction_min,
                    wxt532_direction_avg=wind_sensor_data.direction_avg,
                    wxt532_direction_max=wind_sensor_data.direction_max,
                    wxt532_speed_min=wind_sensor_data.speed_min,
                    wxt532_speed_avg=wind_sensor_data.speed_avg,
                    wxt532_speed_max=wind_sensor_data.speed_max,
                    wxt532_last_update_time=wind_sensor_data.last_update_time,
                ),
            )
        else:
            self.logger.info(f"did not receive any wind sensor measurement")

    def _send_wind_sensor_status(
            self, wind_sensor_status: sensor_types.WindSensorStatus) -> None:
        # send latest wind sensor device info
        if wind_sensor_status is not None:
            self.logger.info(
                f"latest wind sensor device info: {wind_sensor_status}")

            self.message_queue.enqueue_message(
                timestamp=int(time.time()),
                payload=mqtt_playload_types.MQTTWindSensorInfo(
                    wxt532_temperature=wind_sensor_status.temperature,
                    wxt532_heating_voltage=wind_sensor_status.heating_voltage,
                    wxt532_supply_voltage=wind_sensor_status.supply_voltage,
                    wxt532_reference_voltage=wind_sensor_status.
                    reference_voltage,
                    wxt532_last_update_time=wind_sensor_status.
                    last_update_time,
                ),
            )

        else:
            self.logger.info(f"did not receive any wind sensor device info")
