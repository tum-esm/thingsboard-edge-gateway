from typing import Optional
import pydantic


class State(pydantic.BaseModel):
    """Persisting values over program executions."""
    last_upgrade_time: Optional[float]
    last_calibration_time: Optional[float]
    current_config_revision: int
    next_calibration_cylinder: int = pydantic.Field(..., ge=0, le=3)
