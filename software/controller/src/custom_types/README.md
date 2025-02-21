# Custom Types

This directory defines structured data types used throughout the project. These types ensure **type safety, validation, and serialization** for different parts of the system, such as **sensor data, system state, MQTT messages, and configuration parameters**.

## File Structure

```bash
📁 custom/types
    📄 config_types.py            # Configuration file structure
    📄 mqtt_payload_types.py      # MQTT message format definitions
    📄 sensor_types.py            # Sensor data structures
    📄 state_types.py             # Persistent system state
```

## Type Definitions Overview

### **1️⃣ Configuration Types (`config_types.py`)**
Defines the structure for the **system configuration file (`config.json`)**, using **Pydantic** for runtime validation.

#### **Main Components:**
- `ActiveComponentsConfig` → Enables/disables system features (calibration, logging, MQTT).
- `CalibrationConfig` → Specifies gas cylinder calibration settings.
- `DocumentationConfig` → Stores metadata like **site name, sensor IDs, and observation history**.
- `HardwareConfig` → Defines **hardware pin mappings, serial ports, and sensor settings**.
- `MeasurementConfig` → Controls **measurement duration and valve assignments**.
- `Config` → **Top-level structure** for managing the entire `config.json` file.

#### **Purpose:**
✅ Ensures **valid configuration files** via **Pydantic validation**.  
✅ Prevents invalid values for calibration, hardware settings, and measurement control.  

---

### **2️⃣ MQTT Payload Types (`mqtt_payload_types.py`)**
Defines structured **MQTT message formats** for data transmission.

#### **Main Components:**
- `MQTTLogMessage` → Logs messages sent to the server (INFO, WARNING, ERROR).
- `MQTTCO2Data` → Sends **CO₂ sensor readings** (raw, compensated, filtered).
- `MQTTCO2CalibrationData` → Transmits **CO₂ calibration data**.
- `MQTTCalibrationCorrectionData` → Stores calibration correction values.
- `MQTTSystemData` → Reports **system health metrics** (CPU, disk, UPS).
- `MQTTWindData` → Contains **wind speed and direction** information.
- `MQTTWindSensorInfo` → Stores metadata about the **wind sensor’s status**.

#### **Purpose:**
✅ Standardizes **MQTT messages** for logging, sensor readings, and system status.  
✅ Ensures **consistent field names** for ThingsBoard or any MQTT-based platform.  

---

### **3️⃣ Sensor Types (`sensor_types.py`)**
Defines structured **sensor data models** using Python `dataclasses`.

#### **Main Components:**
- `CO2SensorData` → Stores **CO₂ sensor readings** (raw, compensated, filtered).
- `BME280SensorData` → Stores **temperature, humidity, and pressure** readings.
- `SHT45SensorData` → Stores **humidity and temperature** data.
- `UPSSensorData` → Tracks **UPS power state, charge status, and errors**.
- `WindSensorData` → Tracks **wind speed and direction measurements**.
- `WindSensorStatus` → Tracks **wind sensor diagnostics (voltage, temperature, updates).**

#### **Purpose:**
✅ Encapsulates **sensor readings** in structured objects.  
✅ Reduces **code complexity** by providing clear attribute names.  

---

### **4️⃣ State Types (`state_types.py`)**
Defines the structure for the **persistent system state file (`state.json`)**, using **Pydantic** for runtime validation.

#### **Main Components:**
- `State` → Stores **calibration history, humidity offsets, and CO₂ sensor corrections**.

#### **Purpose:**
✅ Ensures **critical system values persist across reboots**.  
✅ Provides **validation and constraints** for stored values.  

---

## **Usage**
### **Importing Types**
To use a type in another module:
```python
from custom.types.config_types import Config
from custom.types.sensor_types import CO2SensorData
from custom.types.mqtt_payload_types import MQTTSystemData
```

### **Validation with Pydantic**
Example: Loading a config file into a `Config` model.
```python
from custom.types.config_types import Config
import json

with open("config.json", "r") as f:
    config_data = json.load(f)

config = Config(**config_data)  # Validates data automatically
```

---

## **Summary**
✅ **Standardized Data Models** → Ensures structured, validated data.  
✅ **Prevents Errors** → Enforces constraints on **MQTT messages, sensor readings, and configs**.  
✅ **Improves Code Maintainability** → Self-explanatory structures simplify development.  

<br>

---
For further details, refer to the individual type definition files.

