from abc import ABC, abstractmethod
import time
from typing import Any, Optional
try:
    import gpiozero.pins.pigpio
except Exception:
    pass

from custom_types import config_types
from interfaces import logging_interface


class Actor(ABC):
    """Abstract base class for a generic actor."""

    class ActorError(Exception):
        """Raised when an error occurs in the actor class."""

    def __init__(
            self,
            config: config_types.Config,
            max_retries: int = 3,
            retry_delay: float = 0.5,
            pin_factory: Optional[gpiozero.pins.pigpio.PiGPIOFactory] = None):

        # init parameters
        self.config = config
        self.simulate = config.active_components.simulation_mode
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.pin_factory = pin_factory

        # init logger with actor class name
        self.logger = logging_interface.Logger(
            config=config, origin=f"{self.__class__.__name__}")

        if self.simulate:
            self.logger.info(f"Simulating {self.__class__.__name__}.")
            return

        self.logger.info("Starting initialization.")
        self._initialize_actor()
        self.logger.info("Finished initialization.")

    def set_with_retry(self,
                       timeout: float = 10,
                       *args: Any,
                       **kwargs: Any) -> Any:
        """Set the actor input with retries, passing dynamic arguments.
        Raises SimulatedValue if the actor is in simulation mode.
        Raises ActorError if all retries fail."""

        start_time = time.time()
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.debug(
                    f"Attempt {attempt} of {self.max_retries}: Setting actor input."
                )
                return self.set(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt} failed: {e}")
                if timeout and time.time() - start_time > timeout:
                    raise self.ActorError("Set retries exceeded timeout.")
                if attempt < self.max_retries:
                    self.reset_actor()
                    self.logger.info(
                        f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.exception(
                        e, label="All retries failed. Raising exception.")
                    raise self.ActorError("All retries failed.")

    def set(self, *args: Any, **kwargs: Any) -> Any:
        """Set the actor input.
        Raises SimulatedValue if the actor is in simulation mode.
        Raises ActorError if the set fails."""

        if self.simulate:
            self.logger.info("Simulating set.")
            return self._simulate_set(*args, **kwargs)

        try:
            return self._set(*args, **kwargs)

        except Exception as e:
            self.logger.exception(e, label="Could not set actor.")
            raise self.ActorError("Could not set actor.")

    def reset_actor(self) -> None:
        """Reset the actor by shutting it down and reinitializing it."""

        if self.simulate:
            self.logger.info("Simulating actor reset.")
            return

        self.logger.info("Starting actor shutdown.")
        self._shutdown_actor()
        self.logger.info("Finished actor shutdown.")
        time.sleep(1)
        self.logger.info("Starting initialization.")
        self._initialize_actor()
        self.logger.info("Finished initialization.")
        time.sleep(1)

    def teardown(self) -> None:
        """Shutdown the actor and close all interfaces."""
        if self.simulate:
            self.logger.info("Simulating actor teardown.")
            return

        self.logger.info("Starting actor teardown.")
        self._shutdown_actor()
        self.logger.info("Finished actor teardown.")

    def check_errors(self) -> None:
        """Check for any errors that might have occurred."""
        if self.simulate:
            self.logger.warning("No errors present in simulation mode.")

        self._check_errors()
        self.logger.info("No errors detected.")

    def _check_errors(self) -> None:
        """Abstract method to check for errors. Can be overridden by subclasses."""
        pass

    def _simulate_set(self, *args: Any, **kwargs: Any) -> Any:
        """Generate a simulated return. Can be overridden by subclasses."""
        return None

    @abstractmethod
    def _initialize_actor(self) -> None:
        """Initializes the actor and sets up all interfaces and connections.
        Is called by the constructor and the method reset_actor."""
        pass

    @abstractmethod
    def _shutdown_actor(self) -> None:
        """Closes all interfaces and connections.
        Is called by the methods reset_actor and teardown."""
        pass

    @abstractmethod
    def _set(self, *args: Any, **kwargs: Any) -> Any:
        """Sets the actor input.
        Needs to raise an exception if the set fails.
        Is called by the methods set and set_with_retry."""
        pass
