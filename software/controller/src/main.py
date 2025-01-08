import os
import signal
import time
import dotenv
from typing import Any

import interfaces, procedures, utils

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run() -> None:
    """Entry point for the measurement automation

    (e) Indicates possibility of an exception that blocks further execution

    INIT

    - State Interface
    - Timeouts
    - Initialize Hardware Interface (e)
    - Initialize Procedures (e) (System Checks, Measurement, Calibration)

    RUN INFINITE MAIN LOOP
    - Procedure: System Check
    - Procedure: Calibration
    - Procedure: Measurements (CO2, Wind)
    """

    dotenv.load_dotenv(os.path.join(PROJECT_DIR, "config", ".env"))
    simulate = os.environ.get("ACROPOLIS_MODE") == "simulate"

    logger = interfaces.Logger(origin="main",
                               print_to_console=simulate
                               or os.environ.get("ACROPOLIS_LOG_TO_CONSOLE"))
    logger.horizontal_line()

    try:
        config = interfaces.ConfigInterface.read()
    except Exception as e:
        logger.exception(e, label="could not load local config.json")
        raise e

    logger.info(
        f"Started new automation process with SW version {config.version} and PID {os.getpid()}.",
        forward=True,
    )

    # -------------------------------------------------------------------------

    # check and provide valid state file
    interfaces.StateInterface.init()

    # define timeouts for parts of the automation
    max_setup_time = 180
    max_system_check_time = 180
    max_calibration_time = ((len(config.calibration.gas_cylinders) + 1) *
                            config.calibration.sampling_per_cylinder_seconds +
                            300  # flush time
                            + 180  # extra time
                            )
    max_measurement_time = config.measurement.procedure_seconds + 180  # extra time
    utils.set_alarm(max_setup_time, "setup")

    # Exponential backoff time
    ebo = utils.ExponentialBackOff()

    # -------------------------------------------------------------------------
    # initialize all hardware interfaces
    # tear down hardware on program termination

    logger.info("Initializing hardware interfaces.", forward=True)

    try:
        hardware_interface = interfaces.HardwareInterface(config=config,
                                                          simulate=simulate)
    except Exception as e:
        logger.exception(e,
                         label="Could not initialize hardware interface.",
                         forward=True)
        raise e

    # tear down hardware on program termination
    def _graceful_teardown(*_args: Any) -> None:
        utils.set_alarm(10, "graceful teardown")

        logger.info("Starting graceful teardown.")
        hardware_interface.teardown()
        logger.info("Finished graceful teardown.")
        exit(0)

    signal.signal(signal.SIGINT, _graceful_teardown)
    signal.signal(signal.SIGTERM, _graceful_teardown)
    logger.info("Established graceful teardown hook.")

    # -------------------------------------------------------------------------
    # initialize procedures

    # initialize procedures interacting with hardware:
    #   system_check:   logging system statistics and reporting hardware/system errors
    #   calibration:    using the two reference gas bottles to calibrate the CO2 sensor
    #   measurements:   do regular measurements for x minutes

    logger.info("Initializing procedures.", forward=True)

    try:
        system_check_procedure = procedures.SystemCheckProcedure(
            config, hardware_interface, simulate=simulate)
        calibration_procedure = procedures.CalibrationProcedure(
            config, hardware_interface, simulate=simulate)
        wind_measurement_procedure = procedures.WindMeasurementProcedure(
            config, hardware_interface, simulate=simulate)
        co2_measurement_procedure = procedures.CO2MeasurementProcedure(
            config, hardware_interface, simulate=simulate)
    except Exception as e:
        logger.exception(e,
                         label="could not initialize procedures",
                         forward=True)
        raise e

    # -------------------------------------------------------------------------
    # infinite mainloop

    logger.info("Successfully finished setup, starting mainloop.",
                forward=True)

    last_successful_mainloop_iteration_time = 0.0
    while True:
        try:
            logger.info("Starting mainloop iteration.")

            # -----------------------------------------------------------------
            # SYSTEM CHECKS

            utils.set_alarm(max_system_check_time, "system check")

            logger.info("Running system checks.")
            system_check_procedure.run()

            # -----------------------------------------------------------------
            # CALIBRATION

            utils.set_alarm(max_calibration_time, "calibration")

            if config.active_components.run_calibration_procedures:
                if calibration_procedure.is_due():
                    logger.info("Running calibration procedure.", forward=True)
                    calibration_procedure.run()
                else:
                    logger.info("Calibration procedure is not due.")
            else:
                logger.info("Skipping calibration procedure due to config.")

            # -----------------------------------------------------------------
            # MEASUREMENTS

            utils.set_alarm(max_measurement_time, "measurement")

            # if messages are empty, run regular measurements
            logger.info("Running measurements.")
            wind_measurement_procedure.run()
            co2_measurement_procedure.run()

            # -----------------------------------------------------------------

            logger.info("Finished mainloop iteration.")
            last_successful_mainloop_iteration_time = time.time()

        except Exception as e:
            logger.exception(e, label="exception in mainloop", forward=True)

            # cancel the alarm for too long mainloops
            signal.alarm(0)

            # reboot if exception lasts longer than 12 hours
            if (time.time() -
                    last_successful_mainloop_iteration_time) >= 86400:
                if utils.read_os_uptime() >= 86400:
                    logger.info(
                        "Rebooting because no successful mainloop iteration for 24 hours.",
                        forward=True,
                    )
                    os.system("sudo reboot")
                else:
                    logger.info(
                        "Persistent issue present. Last reboot is less than 24h ago. No action."
                    )

            try:
                # check timer with exponential backoff
                if time.time() > ebo.next_try_timer():
                    ebo.set_next_timer()
                    # reinitialize all hardware interfaces
                    logger.info("Performing hardware reset.", forward=True)
                    hardware_interface.teardown()
                    hardware_interface.reinitialize(config)
                    logger.info("Hardware reset was successful.", forward=True)

            except Exception as e:
                logger.exception(
                    e,
                    label="exception during hard reset of hardware",
                    forward=True,
                )
                exit(1)


if __name__ == "__main__":
    run()
