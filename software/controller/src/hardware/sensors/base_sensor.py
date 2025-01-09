from abc import ABC, abstractmethod
import time
import random
from typing import Any

from src.custom_types import config_types
from src.interfaces import logging_interface


class Sensor(ABC):
    """Abstract base class for a generic sensor."""

    class SensorError(Exception):
        """Raised when an error occurs in the sensor class."""

    def __init__(self,
                 config: config_types.Config,
                 testing: bool = False,
                 simulate: bool = False,
                 max_retries: int = 3,
                 retry_delay: float = 0.5):

        # init parameters
        self.config = config
        self.simulate = simulate
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # init logger with sensor class name
        self.logger = logging_interface.Logger(
            origin=f"{self.__class__.__name__}",
            print_to_console=testing,
            write_to_file=(not testing),
        )

        if self.simulate:
            self.logger.info(f"Simulating {self.__class__.__name__}.")
            return

        self.logger.info("Starting initialization.")
        self._initialize_sensor()
        self.logger.info("Finished initialization.")

    def read_with_retry(self,
                        timeout: float = 10,
                        *args: Any,
                        **kwargs: Any) -> Any:
        """Read the sensor value with retries, passing dynamic arguments.
        Raises SimulatedValue if the sensor is in simulation mode.
        Raises SensorError if all retries fail."""

        start_time = time.time()
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(
                    f"Attempt {attempt} of {self.max_retries}: Reading sensor value."
                )
                return self.read(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt} failed: {e}")
                if timeout and time.time() - start_time > timeout:
                    raise self.SensorError("Read retries exceeded timeout.")
                if attempt < self.max_retries:
                    self.reset_sensor()
                    self.logger.info(
                        f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.exception(
                        e, label="All retries failed. Raising exception.")
                    raise self.SensorError("All retries failed.")

    def read(self, *args: Any, **kwargs: Any) -> Any:
        """Read the sensor value and forward dynamic arguments to _read.
        Raises SimulatedValue if the sensor is in simulation mode.
        Raises SensorError if the read fails."""

        if self.simulate:
            self.logger.info("Simulating read.")
            return self._simulate_read(*args, **kwargs)

        try:
            answer = self._read(*args, **kwargs)
            return {"value": answer, "simulated": False}
        except Exception as e:
            self.logger.exception(e, label="Could not read sensor data.")
            raise self.SensorError("Could not read sensor data.")

    def reset_sensor(self) -> None:
        """Reset the sensor by shutting it down and reinitializing it."""

        if self.simulate:
            self.logger.info("Simulating sensor reset.")
            return

        self.logger.info("Starting sensor shutdown.")
        self._shutdown_sensor()
        self.logger.info("Finished sensor shutdown.")
        time.sleep(0.5)
        self.logger.info("Starting initialization.")
        self._initialize_sensor()
        self.logger.info("Finished initialization.")

    def _simulate_read(self, *args: Any, **kwargs: Any) -> Any:
        """Generate a simulated read value. Can be overridden by subclasses."""
        return {"value": random.random(), "simulated": True}

    @abstractmethod
    def _initialize_sensor(self) -> None:
        """Initializes the sensor and sets up all interfaces and connections."""
        pass

    @abstractmethod
    def _shutdown_sensor(self) -> None:
        """Closes all interfaces and connections."""
        pass

    @abstractmethod
    def _read(self, *args: Any, **kwargs: Any) -> Any:
        """Needs to raise an exception if the read fails."""
        pass
