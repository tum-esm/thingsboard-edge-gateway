from abc import ABC, abstractmethod
import logging
import time
from typing import Any, Optional


class Actuator(ABC):
    """Abstract base class for a generic actuator.

    Abstract Methods (need to be implemented by subclasses):
        _initialize_actuator: Initializes the actuator and sets up all interfaces and connections.
        _shutdown_actuator: Closes all interfaces and connections.
        _set: Applies the actuator input (subclass-defined).
        _check_errors: Checks for any errors that might have occurred.

    Available Methods:
        set_with_retry: Applies the actuator input with retries.
        set: Applies the actuator input.
        reset_actuator: Resets the actuator by shutting it down and reinitializing it.
        teardown: Shuts down the actuator and closes all interfaces.
        check_errors: Checks for any errors that might have occurred and resets the actuator if necessary.
    """

    class ActuatorError(Exception):
        """Raised when an error occurs in the actuator class."""
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

        # init logger with actuator class name (or injected logger)
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        if self.simulate:
            self.logger.info(f"Simulating {self.__class__.__name__} initialization.")
            return

        self.logger.info("Starting initialization.")
        self._initialize_actuator()
        self.logger.info("Finished initialization.")

    def set_with_retry(
        self,
        timeout: float = 10,
        reduce_logs: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Set the actuator input with retries, passing dynamic arguments.
        Raises ActuatorError if all retries fail.
        """

        start_time = time.time()
        for attempt in range(1, self.max_retries + 1):
            try:
                if not reduce_logs:
                    self.logger.debug(
                        "Attempt %d of %d: Setting actuator input.",
                        attempt,
                        self.max_retries,
                    )
                return self.set(*args, **kwargs)

            except Exception as e:
                self.logger.warning("Attempt %d failed: %s", attempt, e)

                if timeout and time.time() - start_time > timeout:
                    raise self.ActuatorError("Set retries exceeded timeout.") from e

                if attempt < self.max_retries:
                    self.reset_actuator()
                    self.logger.info(
                        "Retrying in %.2f seconds...", self.retry_delay
                    )
                    time.sleep(self.retry_delay)
                else:
                    self.logger.exception("All retries failed. Raising exception.")
                    raise self.ActuatorError("All retries failed.") from e

    def set(self, *args: Any, **kwargs: Any) -> Any:
        """Set the actuator input and forward dynamic arguments to _set.
        Raises ActuatorError if the set fails.
        """

        if self.simulate:
            self.logger.info("Simulating set.")
            return self._simulate_set(*args, **kwargs)

        try:
            return self._set(*args, **kwargs)
        except (BrokenPipeError, ConnectionError) as e:
            self.logger.exception("Lost connection while setting actuator.")
            raise
        except Exception as e:
            self.logger.exception("Could not set actuator.")
            raise self.ActuatorError("Could not set actuator.") from e

    def reset_actuator(self) -> None:
        """Reset the actuator by shutting it down and reinitializing it."""

        if self.simulate:
            self.logger.info("Simulating actuator reset.")
            return

        self.logger.info("Starting actuator shutdown.")
        self._shutdown_actuator()
        self.logger.info("Finished actuator shutdown.")
        time.sleep(1)
        self.logger.info("Starting initialization.")
        self._initialize_actuator()
        self.logger.info("Finished initialization.")
        time.sleep(1)

    def teardown(self) -> None:
        """Shutdown the actuator and close all interfaces."""
        if self.simulate:
            self.logger.info("Simulating actuator teardown.")
            return

        self.logger.info("Starting actuator teardown.")
        self._shutdown_actuator()
        self.logger.info("Finished actuator teardown.")

    def check_errors(self) -> None:
        """Check for any errors that might have occurred."""
        if self.simulate:
            self.logger.debug("No errors present in simulation mode.")
            return

        try:
            self._check_errors()
            self.logger.info("No errors detected.")
        except Exception:
            self.logger.exception("Error detected. Resetting actuator.")
            self.reset_actuator()
            self.logger.info("Error handling completed. Actuator restarted.")
            time.sleep(5)

    def _simulate_set(self, *args: Any, **kwargs: Any) -> Any:
        """Generate a simulated return value. Can be overridden by subclasses."""
        return None

    @abstractmethod
    def _initialize_actuator(self) -> None:
        """Initializes the actuator and sets up all interfaces and connections.
        Is called by the constructor and the method reset_actuator."""
        pass

    @abstractmethod
    def _shutdown_actuator(self) -> None:
        """Closes all interfaces and connections.
        Is called by the methods reset_actuator and teardown."""
        pass

    @abstractmethod
    def _set(self, *args: Any, **kwargs: Any) -> Any:
        """Sets the actuator input.
        Needs to raise an exception if the set fails.
        Is called by the methods set and set_with_retry."""
        pass

    @abstractmethod
    def _check_errors(self) -> None:
        """Abstract method to check for errors. Can be overridden by subclasses."""
        pass
