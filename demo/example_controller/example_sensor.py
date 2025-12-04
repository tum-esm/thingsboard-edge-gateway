import math
import random
import time
from typing import Any, Optional

from ._base_sensor import Sensor


class ExampleSensor(Sensor):
    """
    A simple simulated sensor implementation.
    Produces values that mildly drift over time.
    """

    def __init__(
        self,
        *args,
        simulate: bool,
        **kwargs
    ):
        self._t0 = time.time()
        super().__init__(simulate=simulate, *args, **kwargs)

    def _initialize_sensor(self) -> None:
        """Add your hardware implemenation here."""
        pass

    def _shutdown_sensor(self) -> None:
        """Add your hardware implemenation here."""
        pass
        
    def _read(self, *args: Any, **kwargs: Any) -> None:
        """Add your hardware implemenation here."""
        pass

    def _check_errors(self) -> None:
        """Add your hardware implemenation here."""
        pass
    
    def _simulate_read(self, *args: Any, **kwargs: Any) -> Any:
        """Override base class sensor read simulation."""
        # Time since startup
        t = time.time() - self._t0
        _drift = 0.01  # units per second
        _noise = 0.5   # units

        # Base signal: smooth oscillation
        base = math.sin(t / 3.0) * 10.0

        # A slow drift
        drift_component = _drift * t

        # Random noise
        noise = random.uniform(-_noise, _noise)

        value = base + drift_component + noise

        self.logger.debug(f"ExampleSensor: raw simulated value = {value:.3f}")

        return value
