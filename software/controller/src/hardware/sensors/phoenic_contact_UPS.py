import time
from typing import Optional, Any
try:
    import gpiozero
except Exception:
    pass

from hardware.sensors.base_sensor import Sensor
from custom_types import config_types, sensor_types

UPS_BATTERY_CHARGE_PIN_IN = 5
UPS_POWER_MODE_PIN_IN = 10
UPS_ALARM_PIN_IN = 7


class PhoenixContactUPS(Sensor):
    """Class for the Phoenix Contact Trio-UPS-2G."""

    def __init__(self,
                 config: config_types.Config,
                 pin_factory: gpiozero.pins.pigpio.PiGPIOFactory,
                 simulate: bool = False):
        super().__init__(config=config,
                         pin_factory=pin_factory,
                         simulate=simulate)

    def _initialize_sensor(self) -> None:
        """Initialize the sensor."""

        self.pins: dict[str, gpiozero.DigitalInputDevice] = {
            "UPS_BATTERY_CHARGE_PIN_IN":
            gpiozero.DigitalInputDevice(
                UPS_BATTERY_CHARGE_PIN_IN,
                bounce_time=0.3,
                pin_factory=self.pin_factory,
            ),
            "UPS_POWER_MODE_PIN_IN":
            gpiozero.DigitalInputDevice(
                UPS_POWER_MODE_PIN_IN,
                bounce_time=0.3,
                pin_factory=self.pin_factory,
            ),
            "UPS_ALARM_PIN_IN":
            gpiozero.DigitalInputDevice(
                UPS_ALARM_PIN_IN,
                bounce_time=0.3,
                pin_factory=self.pin_factory,
            )
        }

    def _shutdown_sensor(self) -> None:
        """Shutdown the sensor."""

        for pin in self.pins.values():
            # Shut down the device and release all associated resources (such as GPIO pins).
            pin.close()

    def _read(self, *args: Any, **kwargs: Any) -> sensor_types.UPSSensorData:
        """Read the sensor value."""

        ups_powered_by_grid = self._read_power_mode()
        battery_is_fully_charged = self._read_battery_charge_state()
        battery_error_detected = self._read_alarm_state()
        battery_above_voltage_threshold = self._read_voltage_threshold_state(
            ups_powered_by_grid=ups_powered_by_grid,
            battery_is_fully_charged=battery_is_fully_charged)

        return sensor_types.UPSSensorData(
            ups_powered_by_grid=ups_powered_by_grid,
            ups_battery_is_fully_charged=battery_is_fully_charged,
            ups_battery_error_detected=battery_error_detected,
            ups_battery_above_voltage_threshold=battery_above_voltage_threshold
        )

    def _simulate_read(self, *args: Any,
                       **kwargs: Any) -> sensor_types.UPSSensorData:
        """Simulate the sensor value."""
        return sensor_types.UPSSensorData(
            ups_powered_by_grid=True,
            ups_battery_is_fully_charged=True,
            ups_battery_error_detected=False,
            ups_battery_above_voltage_threshold=True)

    def _read_power_mode(self) -> bool:
        """
        UPS_POWER_MODE_PIN_IN is HIGH when the system is powered by the battery
        UPS_POWER_MODE_PIN_IN is LOW when the system is powered by the grid
        """

        if not self.pins["UPS_POWER_MODE_PIN_IN"].is_active:
            self.logger.info("System is powered by the grid")
            return True
        else:
            self.logger.info("System is powered by the battery")
            return False

    def _read_battery_charge_state(self) -> bool:
        """
        UPS_BATTERY_CHARGE_PIN_IN is HIGH when the battery is fully charged
        UPS_BATTERY_CHARGE_PIN_IN is LOW when the battery is not fully charged
        """

        if self.pins["UPS_BATTERY_CHARGE_PIN_IN"].is_active:
            self.logger.info("The battery is fully charged")
            return True
        else:
            self.logger.info("The battery is not fully charged")
            return False

    def _read_alarm_state(self) -> bool:
        """
        UPS_ALARM_PIN_IN is HIGH when a battery error is detected
        UPS_ALARM_PIN_IN is LOW when the battery status is okay"
        """

        if not self.pins["UPS_ALARM_PIN_IN"].is_active:
            self.logger.info("The battery status is fine")
            return False
        else:
            self.logger.info("A battery error was detected")
            return True

    def _read_voltage_threshold_state(self, ups_powered_by_grid: bool,
                                      battery_is_fully_charged: bool) -> bool:
        """When UPS_STATUS_READY is HIGH & UPS_POWER_MODE_PIN_IN is HIGH
        the battery voltage has dropped below the minimum threshold.
        """

        if ups_powered_by_grid & battery_is_fully_charged:
            self.logger.info(
                "The battery voltage has dropped below the minimum threshold")
            return False
        else:
            self.logger.info(
                "The battery voltage is above the minimum threshold")
            return True
