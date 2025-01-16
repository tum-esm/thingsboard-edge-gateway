import pytest
from unittest.mock import call, patch, MagicMock
from hardware.sensors import base_sensor
from hardware.sensors.vaisala_gmp343 import VaisalaGMP343, CO2_MEASUREMENT_REGEX
from interfaces import config_interface
from custom_types import sensor_types


# Fixture to mock gpiozero OutputDevice
@pytest.fixture
def mock_gpiozero():
    with patch('gpiozero.OutputDevice',
               autospec=True) as mock_output_device_class:
        mock_output_device = MagicMock()
        mock_output_device_class.return_value = mock_output_device
        yield mock_output_device


# Fixture to mock the SerialCO2SensorInterface
@pytest.fixture
def mock_serial_interface():
    mock_serial = MagicMock()
    mock_serial.send_command.return_value = (
        "success", "400.0 395.0 390.0 25.0 (R C C+F T)")
    mock_serial.wait_for_answer.return_value = (
        "success",
        "GMP343 - Version STD 2.0\r\nCopyright: Vaisala Oyj 2003 - 2006")
    return mock_serial


# Fixture to provide a mock configuration
@pytest.fixture
def mock_config():
    config = config_interface.ConfigInterface.read()
    # Customize config for testing
    config.hardware.gmp343_serial_port = "/dev/ttyTEST"
    config.hardware.gmp343_power_pin_out = 20
    return config


# Fixture to create the sensor with mocked dependencies
@pytest.fixture
def sensor(mock_gpiozero, mock_config, mock_serial_interface):
    with patch(
            "hardware.sensors.vaisala_gmp343.serial_interfaces.SerialCO2SensorInterface",
            return_value=mock_serial_interface):
        return VaisalaGMP343(config=mock_config, pin_factory=mock_gpiozero)


# Test Case: Sensor Initialization
def test_config_usage(mock_config, sensor):
    """Test if configuration values are used correctly."""
    assert sensor.config.hardware.gmp343_serial_port == "/dev/ttyTEST"


def test_initialize_sensor(sensor, mock_serial_interface):
    """Test sensor initialization."""
    # Verify that power_pin.on() was called once
    sensor.power_pin.on.assert_called_once()

    # Verify the startup regex validation
    expected_startup_message = "GMP343 - Version STD 2.0\r\nCopyright: Vaisala Oyj 2003 - 2006"
    assert mock_serial_interface.send_command.call_count == 12
    assert mock_serial_interface.wait_for_answer.call_count == 1
    assert mock_serial_interface.wait_for_answer.return_value[
        1] == expected_startup_message


def test_wrong_startup_message(mock_config, mock_gpiozero):
    """Test sensor initialization with wrong startup message."""
    mock_serial = MagicMock()
    mock_serial.wait_for_answer.return_value = (
        "success", "This is not the expected startup message.")

    with patch(
            "hardware.sensors.vaisala_gmp343.serial_interfaces.SerialCO2SensorInterface",
            return_value=mock_serial):
        with pytest.raises(base_sensor.Sensor.SensorError,
                           match="Sending command failed"):
            VaisalaGMP343(config=mock_config, pin_factory=mock_gpiozero)


def test_shutdown_sensor(sensor):
    """Test sensor shutdown."""
    # Arrange: Set the initial state of the mocked power pin
    sensor.power_pin.closed = False  # Ensure the pin is not closed

    # Act: Shut down the sensor
    sensor._shutdown_sensor()

    # Assert: Verify that power_pin.off() and power_pin.close() were called
    sensor.power_pin.off.assert_called_once()
    sensor.power_pin.close.assert_called_once()


def test_shutdown_sensor_already_closed(sensor):
    """Test sensor shutdown when power_pin is already closed."""
    # Arrange: Set the initial state of the mocked power pin
    sensor.power_pin.closed = True  # Simulate already closed pin

    # Act: Shut down the sensor
    sensor._shutdown_sensor()

    # Assert: Verify that power_pin.off() and power_pin.close() were NOT called
    sensor.power_pin.off.assert_not_called()
    sensor.power_pin.close.assert_not_called()


def test_read(sensor, mock_serial_interface):
    """Test reading sensor data."""
    # Mock send_command to return a successful response

    result = sensor.read_with_retry()
    assert isinstance(result, sensor_types.CO2SensorData)
    assert result.raw == 400.0
    assert result.compensated == 395.0
    assert result.filtered == 390.0
    assert result.temperature == 25.0


def test_read_with_retry(sensor, mock_serial_interface):
    """Test reading sensor data with retry and count send_command repetitions."""
    # Mock the _initialize_sensor method to skip actual initialization
    with patch.object(sensor, "_initialize_sensor", return_value=None):
        # Define a side_effect for send_command to simulate retries
        mock_serial_interface.send_command.side_effect = [
            ("timeout", ""),  # First call times out
            ("success",
             "400.0 395.0 390.0 25.0 (R C C+F T)"),  # Second call succeeds
        ]

        # Run the method under test
        result = sensor.read_with_retry()

        # Validate the result
        assert isinstance(result, sensor_types.CO2SensorData)
        assert result.raw == 400.0
        assert result.compensated == 395.0
        assert result.filtered == 390.0
        assert result.temperature == 25.0

        # Assert the number of send_command calls
        assert mock_serial_interface.send_command.call_count == 12 + 2

        # Verify the order of calls
        expected_calls = [
            call("send", expected_regex=CO2_MEASUREMENT_REGEX, timeout=15),
            call("send", expected_regex=CO2_MEASUREMENT_REGEX, timeout=15),
        ]
        mock_serial_interface.send_command.assert_has_calls(expected_calls,
                                                            any_order=False)


def test_read_with_retry_failure(sensor, mock_serial_interface):
    """Test reading sensor data when all retries fail."""
    with patch.object(sensor, "_initialize_sensor", return_value=None):
        # Mock send_command to fail for all attempts
        mock_serial_interface.send_command.side_effect = [
            ("timeout", ""),
            ("timeout", ""),
            ("timeout", ""),
        ]

        with pytest.raises(base_sensor.Sensor.SensorError,
                           match='All retries failed.'):
            sensor.read_with_retry()

        # Assert the number of send_command calls
        assert mock_serial_interface.send_command.call_count == 12 + 3
