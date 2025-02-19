# Procedures

This directory contains procedural implementations for system operations, such as **calibration, measurement, and system health checks**. These procedures are core components of the **main automation loop** in `main.py`, ensuring continuous monitoring, accurate sensor readings, and periodic calibration.

## File Structure

```bash
📁 procedures
    📄 calibration.py      # Handles CO₂ sensor calibration
    📄 measurement.py      # Performs regular CO₂, wind, and auxiliary measurements
    📄 system_checks.py    # Monitors system health and logs diagnostics
```

## Role in the Main Program (`main.py`)

Each procedure is initialized in `main.py` and executed sequentially in an **infinite loop**:

1. **System Checks** → Validate system health before measurements.
2. **Calibration** → Adjust sensor accuracy if calibration is due.
3. **Measurements** → Capture CO₂, wind, and auxiliary environmental data.

The **main loop handles failures** using:

- **Alarms** → Timeouts prevent procedures from stalling the system.
- **Exponential Backoff** → Retries failed operations with increasing delay.
- **Hardware Reinitialization** → Attempts recovery before exiting the current main loop execution.

## Configuration Options

Each procedure supports configurable options defined in the **config.json** file under `active_components`. These options allow enabling or disabling certain features dynamically without modifying the source code.

Users can configure the system by modifying `config.json` and setting parameters under `active_components`. This ensures flexibility in deployment scenarios.

---

## Procedure Descriptions

### **1️⃣ Calibration Procedure (`calibration.py`)**

This procedure manages the **CO₂ sensor calibration process**, ensuring that measurements remain accurate over time. It runs at scheduled intervals, alternating between gas cylinders to optimize gas usage and ensure both are emptied evenly. The first bottle is used longer, including a drying period for internal tubing. The procedure also includes a system flushing phase to remove residual gases before switching bottles and after calibration.

#### **Key Features:**

✅ Ensures accurate CO₂ measurements by periodic calibration.  
✅ Alternates between gas cylinders for even usage and gas conservation.  
✅ (Optional) Calculates calibration correction parameters and persists them across reboots.  
✅ (Optional) Performs a zero-point calibration for the humidity sensor during the calibration run.  
✅ Sends real-time measurement data over **MQTT**

#### **Optional Configurations (`active_components`)**

- **`run_calibration_procedures`** → Toggles whether the calibration procedure runs at scheduled intervals.
- **`perform_sht45_offset_correction`** → Enables or disables humidity offset correction for the **SHT45 sensor**.
- **`perform_co2_calibration_correction`** → Enables or disables local calculation for calibration intercept and slope.

---

### **2️⃣ Measurement Procedure (`measurement.py`)**

This procedure is responsible for conducting **regular CO₂, and wind measurements** while monitoring conditions such as humidity, pressure, and temperature. It offers the option to apply on-device calibration and dilution correction and transmits the collected data over MQTT for real-time monitoring. The measurement interval, duration, and processing methods are defined in the system configuration.

#### **Key Features:**

✅ Measures **CO₂ concentration** (raw, compensated, filtered).  
✅ Collects **wind speed, wind direction, humidity, pressure, and temperature**.  
✅ (Optional) Integrates **post processing logic** for dilution and calibration correction.  
✅ Sends real-time measurement data over **MQTT**

#### **Optional Configurations (`active_components`)**

- **`perform_co2_calibration_correction`** → Enables or disables application of calibration correction.

---

### **3️⃣ System Check Procedure (`system_checks.py`)**

This procedure continuously monitors **system health metrics**, including CPU temperature, disk usage, memory consumption, and power status. It logs these metrics and sends status updates via MQTT, helping detect potential hardware issues.

#### **Key Features:**

✅ Logs **CPU temperature, disk usage, memory consumption, and power status**.  
✅ Helps detect early warnings of hardware or resource exhaustion.  
✅ Checks environmental conditions inside the system enclosure.  
✅ Sends real-time measurement data over **MQTT**

---

## **Usage**

### **Running Procedures in Code**

Each procedure can be triggered programmatically by instantiating the respective class and calling `run()`.

Example for measurement:

```python
from procedures.measurement import MeasurementProcedure
from interfaces.hardware_interface import HardwareInterface
from custom_types.config_types import Config

config = config_interface.ConfigInterface.read()  # Load config
hardware = HardwareInterface(config=config)
measurement = MeasurementProcedure(config=config, hardware_interface=hardware)
measurement.run()
```

---

## **Summary**

✅ **Automates Key System Functions** → Calibration, measurement, and system monitoring.  
✅ **Ensures Sensor Accuracy** → Regular calibration and real-time measurements.  
✅ **Logs System Health** → Tracks **CPU, disk, memory, and UPS status** for diagnostics.  
✅ **Captures Atmospheric Data** → Measures **CO₂, wind, humidity, pressure, and temperature**.  
✅ **Configurable via `active_components`** → Enables/disables optional features dynamically.  
✅ **Integrated with `main.py`** → Seamlessly runs in an infinite loop with fail-safes.

For further details, refer to the individual procedure files.
