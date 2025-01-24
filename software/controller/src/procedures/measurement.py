import time
from typing import Optional, Literal

from custom_types import config_types
from interfaces import hardware_interface, logging_interface


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
        self.active_air_inlet: Optional[Literal[1, 2, 3, 4]] = None
        self.last_measurement_time: float = 0
        self.hardware_interface = hardware_interface

    def run(self) -> None:
        """
        1. Collect Wind Sensor Data
        2. Run CO2 sensor measurement interval
        """
        # Ensure that measurement line is active
        if not (self.hardware_interface.valves.active_input
                == self.config.measurement.valve_number):
            self.hardware_interface.valves.set(
                number=self.config.measurement.valve_number)

        # Wind sensor data
        self.hardware_interface.wind_sensor_module.process_wind_sensor_data()

        # do regular measurements for in config defined measurement interval
        self.logger.info(
            f"starting {self.config.measurement.procedure_seconds} seconds long CO2 measurement interval"
        )
        self._co2_measurement_interval()
        self.logger.info(f"finished CO2 measurement interval")

    def _co2_measurement_interval(self) -> None:
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

            # perform a CO2 measurement
            measurement = self.hardware_interface.co2_measurement_module.perform_CO2_measurement(
            )

            # perform edge correction
            if self.config.active_components.perform_co2_calibration_correction:
                gmp343_edge_dry, gmp343_edge_corrected = self.hardware_interface.co2_measurement_module.perform_edge_correction(
                    CO2_sensor_data=measurement)
            else:
                gmp343_edge_dry, gmp343_edge_corrected = None, None

            # send out measurement data
            self.hardware_interface.co2_measurement_module.send_CO2_measurement_data(
                CO2_sensor_data=measurement,
                edge_dry=gmp343_edge_dry,
                edge_corrected=gmp343_edge_corrected)

            # stop loop after defined measurement interval
            if (self.last_measurement_time - measurement_procedure_start_time
                ) >= self.config.measurement.procedure_seconds:
                break
