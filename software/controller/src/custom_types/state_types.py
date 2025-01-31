from typing import Optional
import pydantic


class State(pydantic.BaseModel):
    """Persisting values over program executions."""
    last_calibration_attempt: Optional[float]
    next_calibration_cylinder: int = pydantic.Field(..., ge=0, le=3)
    sht45_humidity_offset: float
    co2_sensor_intercept: float
    co2_sensor_slope: float
