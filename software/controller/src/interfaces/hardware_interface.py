import os
from typing import TypedDict
import filelock

from src.interfaces import logging_interface
from src.custom_types import config_types
from src.hardware.bme280_sensor import BME280SensorInterface
from src.hardware.gmp343_sensor import CO2SensorInterface
from src.hardware.pump import PumpInterface
from src.hardware.sht45_sensor import SHT45SensorInterface
from src.hardware.ups import UPSInterface
from src.hardware.valves import ValveInterface
from src.hardware.wxt532_sensor import WindSensorInterface


class HwLock(TypedDict):
    lock: filelock.FileLock


global_hw_lock: HwLock = {"lock": filelock.FileLock("")}


def acquire_hardware_lock() -> None:
    """make sure that there is only one initialized hardware connection"""
    try:
        global_hw_lock["lock"].acquire()
    except filelock.Timeout:
        raise HardwareInterface.HardwareOccupiedException(
            "hardware occupied by another process")


class HardwareInterface:

    class HardwareOccupiedException(Exception):
        """raise when trying to use the hardware, but it
        is used by another process"""

    def __init__(
        self,
        config: config_types.Config,
        simulate: bool = False,
    ) -> None:
        global_hw_lock["lock"] = filelock.FileLock(
            os.environ.get("ACROPOLIS_HARDWARE_LOCKFILE_PATH")
            or "/home/pi/Documents/acropolis/acropolis-hardware.lock",
            timeout=5,
        )
        self.config = config
        self.logger = logging_interface.Logger("hardware-interface", )
        self.simulate = simulate
        acquire_hardware_lock()

        # measurement sensors
        self.wind_sensor = WindSensorInterface(config, simulate=self.simulate)
        self.air_inlet_bme280_sensor = BME280SensorInterface(
            config, variant="air-inlet", simulate=self.simulate)
        self.air_inlet_sht45_sensor = SHT45SensorInterface(
            config, simulate=self.simulate)
        self.co2_sensor = CO2SensorInterface(config, simulate=self.simulate)

        # measurement actors
        self.pump = PumpInterface(config, simulate=self.simulate)
        self.valves = ValveInterface(config, simulate=self.simulate)

        # enclosure controls
        self.mainboard_sensor = BME280SensorInterface(config,
                                                      variant="ioboard",
                                                      simulate=self.simulate)
        self.ups = UPSInterface(config, simulate=self.simulate)

    def check_errors(self) -> None:
        """checks for detectable hardware errors"""
        self.logger.info("checking for hardware errors")
        self.co2_sensor.check_errors()
        self.wind_sensor.check_errors()

    def teardown(self) -> None:
        """ends all hardware/system connections"""
        self.logger.info("running hardware teardown")

        if not global_hw_lock["lock"].is_locked:
            self.logger.info("not tearing down due to disconnected hardware")
            return

        # measurement sensors
        self.air_inlet_bme280_sensor.teardown()
        self.wind_sensor.teardown()

        # measurement actors
        self.pump.teardown()
        self.valves.teardown()
        self.co2_sensor.teardown()

        # enclosure controls
        self.mainboard_sensor.teardown()
        self.ups.teardown()

        # release lock
        global_hw_lock["lock"].release()

    def reinitialize(self, config: config_types.Config) -> None:
        """reinitialize after an unsuccessful update"""
        self.config = config
        self.logger.info("running hardware reinitialization")
        acquire_hardware_lock()

        # measurement sensors
        self.air_inlet_bme280_sensor = BME280SensorInterface(
            config, variant="air-inlet", simulate=self.simulate)
        self.air_inlet_sht45_sensor = SHT45SensorInterface(
            config, simulate=self.simulate)
        self.co2_sensor = CO2SensorInterface(config, simulate=self.simulate)
        self.wind_sensor = WindSensorInterface(config, simulate=self.simulate)

        # measurement actors
        self.pump = PumpInterface(config, simulate=self.simulate)
        self.valves = ValveInterface(config, simulate=self.simulate)

        # enclosure controls
        self.mainboard_sensor = BME280SensorInterface(config,
                                                      variant="ioboard",
                                                      simulate=self.simulate)
        self.ups = UPSInterface(config, simulate=self.simulate)
