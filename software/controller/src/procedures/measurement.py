from custom_types import config_types
from interfaces import hardware_interface, logging_interface
from hardware.modules import co2_sensor, wind_sensor


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

        # state variables
        self.co2_sensor_module = co2_sensor.CO2MeasurementModule(
            config=config, hardware_interface=hardware_interface)

        self.wind_sensor_module = wind_sensor.WindSensorModule(
            config=config, hardware_interface=hardware_interface)

    def run(self) -> None:
        """
        1. Collect Wind Sensor Data
        2. Run CO2 sensor measurement interval
        """

        # Wind sensor data
        self.wind_sensor_module.process_wind_sensor_data()

        # do regular measurements for in config defined measurement interval
        self.logger.info(
            f"starting {self.config.measurement.procedure_seconds} seconds long CO2 measurement interval"
        )
        self.co2_sensor_module.run_CO2_measurement_interval()
        self.logger.info(f"finished CO2 measurement interval")
