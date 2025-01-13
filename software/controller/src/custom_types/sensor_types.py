from typing import Optional
import pydantic

# validation is only necessary for external sources
# internal source will be covered by mypy


# Sensor data
class CO2SensorData(pydantic.BaseModel):
    raw: float
    compensated: float
    filtered: float
    temperature: float


class BME280SensorData(pydantic.BaseModel):
    """units: °C for temperature, rH for humidity, hPa for pressure"""

    temperature: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]


class SHT45SensorData(pydantic.BaseModel):
    """units: °C for temperature, rH for humidity"""

    temperature: Optional[float]
    humidity: Optional[float]


class UPSSensorData(pydantic.BaseModel):

    ups_powered_by_grid: bool
    ups_battery_is_fully_charged: bool
    ups_battery_error_detected: bool
    ups_battery_above_voltage_threshold: bool


class WindSensorData(pydantic.BaseModel):
    direction_min: float
    direction_avg: float
    direction_max: float
    speed_min: float
    speed_avg: float
    speed_max: float
    last_update_time: float


class WindSensorStatus(pydantic.BaseModel):
    temperature: float
    heating_voltage: float
    supply_voltage: float
    reference_voltage: float
    last_update_time: float
