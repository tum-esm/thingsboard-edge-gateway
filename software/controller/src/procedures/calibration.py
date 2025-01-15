import time
from datetime import datetime

from custom_types import config_types
from interfaces import logging_interface, state_interface, hardware_interface
from utils import message_queue


class CalibrationProcedure:
    """runs when a calibration is due"""

    def __init__(
            self, config: config_types.Config,
            hardware_interface: hardware_interface.HardwareInterface) -> None:
        self.logger, self.config = logging_interface.Logger(
            config=config, origin="calibration-procedure"), config
        self.hardware_interface = hardware_interface

        self.last_measurement_time: float = 0
        self.message_queue = message_queue.MessageQueue()
        self.seconds_drying_with_first_bottle = 0

    def run(self) -> None:
        state = state_interface.StateInterface.read(config=self.config)
        calibration_time = datetime.utcnow().timestamp()
        self.logger.info(
            f"starting calibration procedure at timestamp {calibration_time}",
            forward=True,
        )

        # clear ring buffers
        self.hardware_interface.co2_measurement_module.reset_ring_buffers()

        # alternate calibration bottle order every other day
        # first bottle receives additional time to dry air chamber
        sequence_calibration_bottle = self._alternate_bottle_for_drying()

        for gas in sequence_calibration_bottle:
            # switch to each calibration valve
            self.hardware_interface.valves.set(gas.valve_number)

            self._co2_measurement_interval(gas=gas.valve_number)

            # reset drying time extension for following bottles
            self.seconds_drying_with_first_bottle = 0

        # switch back to measurement inlet
        self.hardware_interface.valves.set(
            self.config.measurement.valve_number)

        # flush the system after calibration at max pump speed
        self.hardware_interface.pump.flush_system(
            duration=self.config.calibration.system_flushing_seconds,
            pwm_duty_cycle=self.config.calibration.
            system_flushing_pump_pwm_duty_cycle,
        )

        # clear ring buffers
        self.hardware_interface.co2_measurement_module.reset_ring_buffers()

        # save last calibration time
        self.logger.debug("updating state")
        self.logger.info(
            f"finished calibration procedure at timestamp {datetime.utcnow().timestamp()}",
            forward=True,
        )
        state = state_interface.StateInterface.read(config=self.config)
        state.last_calibration_time = calibration_time
        state_interface.StateInterface.write(state)

    def is_due(self) -> bool:
        """returns true when calibration procedure should run

        two conditions are checked:
        1. time > last calibration day + x days (config) at time (config)
        2. day of last calibration was not today
        #"""

        # load state, kept during configuration procedures
        state = state_interface.StateInterface.read(config=self.config)
        current_utc_day = datetime.utcnow().date()
        current_utc_hour = datetime.utcnow().hour

        # if last calibration time is unknown, calibrate now
        # only happens when the state.json is recreated
        if state.last_calibration_time is None:
            self.logger.info(
                "last calibration time is unknown, calibrating now")
            return True

        last_calibration_day = datetime.fromtimestamp(
            state.last_calibration_time).date()
        days_since_last_calibration = (current_utc_day -
                                       last_calibration_day).days

        # check if a calibration was already performed on the same day
        if current_utc_day == last_calibration_day:
            self.logger.info("last calibration was already done today")
            return False

        # compare scheduled calibration day to today
        if (days_since_last_calibration
                < self.config.calibration.calibration_frequency_days):
            self.logger.info(f"next scheduled calibration is not due today.")
            return False

        # check if current hour is past the scheduled hour of day
        if current_utc_hour < self.config.calibration.calibration_hour_of_day:
            self.logger.info("next calibration is scheduled for later today")
            return False

        # skip calibration when sensor has had power for less than 30
        # minutes (a full warming up is required for maximum accuracy)
        seconds_since_last_co2_sensor_boot = round(
            time.time() - self.hardware_interface.co2_sensor.last_powerup_time,
            2)
        if seconds_since_last_co2_sensor_boot < 1800:
            self.logger.info(
                f"skipping calibration, sensor is still warming up (co2 sensor"
                + f" booted {seconds_since_last_co2_sensor_boot} seconds ago)")
            return False

        self.logger.info("next calibration is due, calibrating now")
        return True

    def _co2_measurement_interval(self, gas: int) -> None:
        calibration_procedure_start_time = time.time()
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

            measurement = self.hardware_interface.co2_measurement_module.perform_CO2_measurement(
            )
            self.hardware_interface.co2_measurement_module.send_CO2_calibration_data(
                CO2_sensor_data=measurement, gas_bottle_id=gas)

            if ((self.last_measurement_time - calibration_procedure_start_time)
                    >= self.config.calibration.sampling_per_cylinder_seconds +
                    self.seconds_drying_with_first_bottle):
                break

    def _alternate_bottle_for_drying(
            self) -> list[config_types.CalibrationGasConfig]:
        """
        1. sets time for drying the air chamber with first calibration bottle
        2. switches to the next calibration cylinder every other calibration
        """

        # set time extension for first bottle
        self.seconds_drying_with_first_bottle = (
            self.config.calibration.sampling_per_cylinder_seconds)

        # read the latest state
        state = state_interface.StateInterface.read(config=self.config)

        current_position = state.next_calibration_cylinder

        if current_position + 1 < len(self.config.calibration.gas_cylinders):
            next_position = current_position + 1
        else:
            next_position = 0

        # update state config
        state.next_calibration_cylinder = next_position
        state_interface.StateInterface.write(state)

        # update sequence

        # 2 calibration cylinders
        if len(self.config.calibration.gas_cylinders) == 2:
            if current_position == 0:
                return self.config.calibration.gas_cylinders
            if current_position == 1:
                return [
                    self.config.calibration.gas_cylinders[1],
                    self.config.calibration.gas_cylinders[0],
                ]

        # 3 calibration cylinders
        if len(self.config.calibration.gas_cylinders) == 3:
            if current_position == 0:
                return self.config.calibration.gas_cylinders
            if current_position == 1:
                return [
                    self.config.calibration.gas_cylinders[1],
                    self.config.calibration.gas_cylinders[2],
                    self.config.calibration.gas_cylinders[0],
                ]
            if current_position == 2:
                return [
                    self.config.calibration.gas_cylinders[2],
                    self.config.calibration.gas_cylinders[1],
                    self.config.calibration.gas_cylinders[0],
                ]

        # 1 or 4+ calibration cylinders
        return self.config.calibration.gas_cylinders
