from abc import ABC, abstractmethod
import logging
import time
import random
from typing import Any, Optional


class Sensor(ABC):
    """Abstract base class for a generic sensor.
    
    Abstract Methods (need to be implemented by subclasses):
        _initialize_sensor: Initializes the sensor and sets up all interfaces and connections.
        _shutdown_sensor: Closes all interfaces and connections.
        _read: Returns the sensor output.
        _check_errors: Checks for any errors that might have occurred.
        
    Available Methods:
        read_with_retry: Reads the sensor value with retries.
        read: Reads the sensor value.
        reset_sensor: Resets the sensor by shutting it down and reinitializing it.
        teardown: Shuts down the sensor and closes all interfaces.
        check_errors: Checks for any errors that might have occurred and reset the sensor if necessary.
    """

    class SensorError(Exception):
        """Raised when an error occurs in the sensor class."""
        pass

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        simulate: bool = False,
        logger: Optional[logging.Logger] = None,
    ) -> None:

        # init parameters
        self.simulate = simulate
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # init logger with sensor class name (or injected logger)
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        if self.simulate:
            self.logger.info(f"Simulating {self.__class__.__name__} initialization.")
            return

        self.logger.info("Starting initialization.")
        self._initialize_sensor()
        self.logger.info("Finished initialization.")

    def read_with_retry(
        self,
        timeout: float = 10,
        reduce_logs: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Read the sensor value with retries, passing dynamic arguments.
        Raises SensorError if all retries fail.
        """

        start_time = time.time()
        for attempt in range(1, self.max_retries + 1):
            try:
                if not reduce_logs:
                    self.logger.debug(
                        "Attempt %d of %d: Reading sensor value.",
                        attempt,
                        self.max_retries,
                    )
                return self.read(*args, **kwargs)

            except Exception as e:
                self.logger.warning("Attempt %d failed: %s", attempt, e)
                if timeout and time.time() - start_time > timeout:
                    raise self.SensorError("Read retries exceeded timeout.") from e

                if attempt < self.max_retries:
                    self.reset_sensor()
                    self.logger.info(
                        "Retrying in %.2f seconds...", self.retry_delay
                    )
                    time.sleep(self.retry_delay)
                else:
                    self.logger.exception("All retries failed. Raising exception.")
                    raise self.SensorError("All retries failed.") from e

    def read(self, *args: Any, **kwargs: Any) -> Any:
        """Read the sensor value and forward dynamic arguments to _read.
        Raises SensorError if the read fails.
        """

        if self.simulate:
            self.logger.info("Simulating read.")
            return self._simulate_read(*args, **kwargs)

        try:
            return self._read(*args, **kwargs)
        except Exception as e:
            self.logger.exception("Could not read sensor data.")
            raise self.SensorError("Could not read sensor data.") from e

    def reset_sensor(self) -> None:
        """Reset the sensor by shutting it down and reinitializing it."""

        if self.simulate:
            self.logger.info("Simulating sensor reset.")
            return

        self.logger.info("Starting sensor shutdown.")
        self._shutdown_sensor()
        self.logger.info("Finished sensor shutdown.")
        time.sleep(1)
        self.logger.info("Starting initialization.")
        self._initialize_sensor()
        self.logger.info("Finished initialization.")
        time.sleep(1)

    def teardown(self) -> None:
        """Shutdown the sensor and close all interfaces."""
        if self.simulate:
            self.logger.info("Simulating sensor teardown.")
            return

        self.logger.info("Starting sensor teardown.")
        self._shutdown_sensor()
        self.logger.info("Finished sensor teardown.")

    def check_errors(self) -> None:
        """Check for any errors that might have occurred."""
        if self.simulate:
            self.logger.debug("No errors present in simulation mode.")
            return

        try:
            self._check_errors()
            self.logger.info("No errors detected.")
        except Exception:
            self.logger.exception("Error detectedin. Resetting sensor.")
            self.reset_sensor()
            self.logger.info("Error handling completed. Sensor restarted.")
            time.sleep(5)

    def _simulate_read(self, *args: Any, **kwargs: Any) -> Any:
        """Generate a simulated read value. Can be overridden by subclasses."""
        return random.random()

    @abstractmethod
    def _initialize_sensor(self) -> None:
        """Initializes the sensor and sets up all interfaces and connections.
        Is called by the constructor and the method reset_sensor."""
        pass

    @abstractmethod
    def _shutdown_sensor(self) -> None:
        """Closes all interfaces and connections.
        Is called by the methods reset_sensor and teardown."""
        pass

    @abstractmethod
    def _read(self, *args: Any, **kwargs: Any) -> Any:
        """Returns the sensor outout.
        Needs to raise an exception if the read fails.
        Is called by the methods read and read_with_retry."""
        pass

    @abstractmethod
    def _check_errors(self) -> None:
        """Abstract method to check for errors. Can be overridden by subclasses."""
        pass