from typing import Any

from sensor.base_sensor import Sensor


class BasicSensor(Sensor):
    def _shutdown_sensor(self) -> None:
        pass

    def _read(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def _check_errors(self) -> None:
        pass

    def _initialize_sensor(self) -> None:
        pass