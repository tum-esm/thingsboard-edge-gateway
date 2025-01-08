import gpiozero
import gpiozero.pins.pigpio
import time

from src.hardware.sensors.base_sensor import Sensor
from src.custom_types import sensor_types
from src.interfaces import serial_interfaces
from src.utils import gpio_pin_factory

CO2_SENSOR_POWER_PIN_OUT = 20
CO2_SENSOR_SERIAL_PORT = "/dev/ttySC0"
CO2_MEASUREMENT_REGEX = (
    r"\d+\.\d+\s+"  # raw
    + r"\d+\.\d+\s+"  # compensated
    + r"\d+\.\d+\s+"  # compensated + filtered
    + r"\d+\.\d+\s+"  # temperature
    + r"\(R C C\+F T\)")
STARTUP_REGEX = r"GMP343 - Version STD \d+\.\d+\\r\\n" + \
                r"Copyright: Vaisala Oyj \d{4} - \d{4}"


class VaisalaGMP343(Sensor):
    """Class for the Vaisala GMP343 sensor."""

    def __init__(self, config, testing=False, simulate=False):
        super().__init__(config, testing=testing, simulate=simulate)

        # serial connection to receive data from CO2 sensor
        self.serial_interface = serial_interfaces.SerialCO2SensorInterface(
            port=CO2_SENSOR_SERIAL_PORT)

    def _initialize_sensor(self):
        """Initialize the sensor."""
        self.pin_factory = gpio_pin_factory.get_gpio_pin_factory()
        self.power_pin = gpiozero.OutputDevice(pin=CO2_SENSOR_POWER_PIN_OUT,
                                               pin_factory=self.pin_factory)
        self.serial_interface.flush_receiver_stream()
        self.power_pin.on()
        self.last_powerup_time = time.time()
        self.serial_interface.wait_for_answer(expected_regex=STARTUP_REGEX,
                                              timeout=10)

        self._send_sensor_settings()

    def _shutdown_sensor(self):
        """Shutdown the sensor."""

        self.power_pin.off()
        self.pin_factory.close()

    def _read(self, *args, **kwargs):
        """Read the sensor value."""
        humidity = kwargs.get('humidity', None)
        pressure = kwargs.get('pressure', None)

        # set compensation values if provided
        if (humidity is not None) and (pressure is not None):
            self.send_compensation_values(pressure=pressure, humidity=humidity)

        answer = self.serial_interface.send_command(
            "send", expected_regex=CO2_MEASUREMENT_REGEX, timeout=30)
        sensor_data = tuple(map(float, answer.split()[:4]))

        return sensor_types.CO2SensorData(
            raw=sensor_data[0],
            compensated=sensor_data[1],
            filtered=sensor_data[2],
            temperature=sensor_data[3],
        )

    def _send_command_to_sensor(
        self,
        command: str,
        expected_regex: str = r".*\>.*",
        timeout: float = 8,
    ) -> str:
        """Allows to send a full text command to the GMP343 CO2 Sensor.
        Please refer to the user manual for valid commands."""

        answer = self.serial_interface.send_command(
            message=command, expected_regex=expected_regex, timeout=timeout)

        answer[1] = (answer[1].strip(" \r\n").replace("  ", "").replace(
            " : ", ": ").replace(" \r\n",
                                 "\r\n").replace("\r\n\r\n", "\r\n").replace(
                                     "\r\n", "; ").removesuffix("; >"))

        # command was successful
        if answer[0] == "success":
            return answer[1]

        # command returned uncomplete message
        if answer[0] == "uncomplete":
            answer = self.serial_interface.send_command(
                message=command.strip().split(" ")[-1],
                expected_regex=expected_regex,
                timeout=timeout)

            if answer[0] == "success":
                self.logger.info(
                    "Resending value after uncomplete was successful")
                return answer[1]
            else:
                raise self.SensorError(
                    f"Resend failed: uncomplete. Sensor answer: {answer[1]}")

        # command returned timeout message
        if answer[0] == "timeout":
            answer = self.serial_interface.send_command(
                message=command,
                expected_regex=expected_regex,
                timeout=timeout)

            if answer[0] == "success":
                self.logger.info(
                    "Resending command after timeout was successful.")
                return answer[1]
            else:
                raise self.SensorError(
                    f"Resend failed: timeout. Sensor answer: {answer[1]}")

    def _send_sensor_settings(self):

        self._send_command_to_sensor(
            command='form CO2RAWUC CO2RAW CO2 T " (R C C+F T)"')

        self._send_command_to_sensor(command="echo off")

        self._send_command_to_sensor(command=f"range 1")

        value = self.config.hardware.gmp343_filter_seconds_averaging
        self._send_command_to_sensor(command=f"average {value}")

        value = self.config.hardware.gmp343_filter_smoothing_factor
        self._send_command_to_sensor(command=f"smooth {value}")

        value = self.config.hardware.gmp343_filter_median_measurements
        self._send_command_to_sensor(command=f"median {value}")

        setting = self.config.hardware.gmp343_optics_heating
        self._send_command_to_sensor(
            command=f"heat {'on' if setting else 'off'}")

        setting = self.config.hardware.gmp343_linearisation
        self._send_command_to_sensor(
            command=f"linear {'on' if setting else 'off'}")

        setting = self.config.hardware.gmp343_temperature_compensation
        self._send_command_to_sensor(
            command=f"tc {'on' if setting else 'off'}")

        setting = self.config.hardware.gmp343_relative_humidity_compensation
        self._send_command_to_sensor(
            command=f"rhc {'on' if setting else 'off'}")

        setting = self.config.hardware.gmp343_pressure_compensation
        self._send_command_to_sensor(
            command=f"pc {'on' if setting else 'off'}")

        setting = self.config.hardware.gmp343_oxygen_compensation
        self._send_command_to_sensor(
            command=f"oc {'on' if setting else 'off'}")

    def send_compensation_values(self, pressure: float,
                                 humidity: float) -> None:
        """
        update pressure, humidity in sensor
        for its internal compensation.

        the internal temperature compensation is enabled by default
        and uses the built-in temperature sensor.
        """

        assert 0 <= humidity <= 100, f"invalid humidity ({humidity} not in [0, 100])"
        assert (700 <= pressure <=
                1300), f"invalid pressure ({pressure} not in [700, 1300])"

        self._set_sensor_parameter(parameter="rh", value=round(humidity, 2))
        self._set_sensor_parameter(parameter="p", value=round(pressure, 2))

        self.logger.info(
            f"Updated compensation values: pressure = {pressure}, " +
            f"humidity = {humidity}.")

    def check_param_info(self) -> str:
        """runs the "param" command to get a full sensor parameter report"""
        if self.simulate:
            return "Simulated CO2 Sensor"
        try:
            return self._send_command_to_sensor("param")
        except Exception:
            self._reset_sensor()
            return self._send_command_to_sensor("param")

    def check_errors(self) -> None:
        """checks whether the CO2 probe reports any errors. Possibly raises
        the CO2SensorInterface.CommunicationError exception"""
        if self.simulate:
            self.logger.info("The CO2 sensor check doesn't report any errors.")
            return

        answer = self._send_command_to_sensor("errs")

        if not ("OK: No errors detected." in answer):
            self.logger.warning(
                f"The CO2 sensor reported errors: {answer}",
                forward=True,
            )

        self.logger.info("The CO2 sensor check doesn't report any errors.")
