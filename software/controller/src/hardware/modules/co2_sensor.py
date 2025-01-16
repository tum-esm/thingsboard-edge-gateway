from typing import Any
import time

from custom_types import config_types, sensor_types, mqtt_playload_types
from interfaces import logging_interface
from utils import ring_buffer, message_queue
from hardware.sensors.vaisala_gmp343 import VaisalaGMP343
from hardware.sensors.bosch_bme280 import BoschBME280
from hardware.sensors.sensirion_sht45 import SensirionSHT45


class CO2MeasurementModule:
    """Combines sensor and actor interfaces."""

    def __init__(self, config: config_types.Config, co2_sensor: VaisalaGMP343,
                 inlet_bme280: BoschBME280,
                 inlet_sht45: SensirionSHT45) -> None:

        self.logger = logging_interface.Logger(config=config,
                                               origin="CO2MeasurementModule")
        self.config = config
        self.message_queue = message_queue.MessageQueue()
        self.reset_ring_buffers()

        # hardware
        self.co2_sensor = co2_sensor
        self.inlet_bme280 = inlet_bme280
        self.inlet_sht45 = inlet_sht45

    def perform_CO2_measurement(self) -> Any:
        """do regular measurements for in config defined measurement interval"""

        # Get latest auxiliary sensor data information
        self._update_air_inlet_parameters()

        # perform a CO2 measurement
        CO2_sensor_data = (self.co2_sensor.read_with_retry(
            timeout=60,
            pressure=self.rb_pressure.avg(),
            humidity=self.rb_humidity.avg(),
        ))
        self.logger.debug(f"new measurement: {CO2_sensor_data}")

        return CO2_sensor_data

    def _update_air_inlet_parameters(self) -> None:
        """
        fetches the latest temperature and pressure data at air inlet
        """

        self.air_inlet_bme280_data = (self.inlet_bme280.read_with_retry())

        # Add to ring buffer to calculate moving average of low-cost sensor
        self.rb_pressure.append(self.air_inlet_bme280_data.pressure)

        self.air_inlet_sht45_data = (self.inlet_sht45.read_with_retry())

        # Add to ring buffer to calculate moving average of low-cost sensor
        self.rb_humidity.append(self.air_inlet_sht45_data.humidity)

    def reset_ring_buffers(self) -> None:
        self.rb_pressure = ring_buffer.RingBuffer(
            self.config.measurement.average_air_inlet_measurements)
        self.rb_humidity = ring_buffer.RingBuffer(
            self.config.measurement.average_air_inlet_measurements)

    def send_CO2_measurement_data(
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

    def send_CO2_calibration_data(self,
                                  CO2_sensor_data: sensor_types.CO2SensorData,
                                  gas_bottle_id: int) -> None:

        # send out MQTT measurement message
        self.message_queue.enqueue_message(
            timestamp=int(time.time()),
            payload=mqtt_playload_types.MQTTCO2CalibrationData(
                cal_bottle_id=float(gas_bottle_id),
                cal_gmp343_raw=CO2_sensor_data.raw,
                cal_gmp343_compensated=CO2_sensor_data.compensated,
                cal_gmp343_filtered=CO2_sensor_data.filtered,
                cal_bme280_temperature=self.air_inlet_bme280_data.temperature,
                cal_bme280_humidity=self.air_inlet_bme280_data.humidity,
                cal_bme280_pressure=self.air_inlet_bme280_data.pressure,
                cal_sht45_temperature=self.air_inlet_sht45_data.temperature,
                cal_sht45_humidity=self.air_inlet_sht45_data.humidity,
                cal_gmp343_temperature=CO2_sensor_data.temperature,
            ),
        )
