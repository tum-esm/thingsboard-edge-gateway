# Source Code (`src`)

The `src` directory contains the **core software implementation** for the edge controller, including the main execution script and modular components for **hardware control, data processing, system monitoring, and communication**.

## Directory Structure

```bash
📁 src
    📄 main.py          # Entry point for the sensor system
    📁 interfaces       # Hardware & system communication interfaces
    📁 hardware         # Sensor and actuator hardware abstraction
    📁 custom_types     # Data models and structured types
    📁 procedures       # Core operational procedures (calibration, measurement, system checks)
    📁 utils            # Utility functions for data processing, logging, and system handling
```

## **Main Script (`main.py`)**

The **entry point** for the entire system, handling:

- **Initialization of configurations, hardware, and interfaces**
- **Execution of procedures** (calibration, measurement, system checks)
- **Main control loop** to ensure continuous operation
- **Graceful shutdown and error handling**

---

## **Subdirectories Overview**

### **1️⃣ Custom Types (`custom_types/`)**

Defines **structured data models** using `pydantic` and `dataclasses`.

✅ Standardizes **sensor readings, calibration data, and MQTT payloads**.  
✅ Ensures **type safety and validation** for configurations.  
✅ Provides **data integrity for continiuous operation**.

---


### **2️⃣ Hardware (`hardware/`)**

Contains **abstractions for sensors and actuators**, allowing modular hardware integration.

✅ Implements **CO₂ sensor, wind sensor, actuators, and power management**.  
✅ Implements **modules** that bundles sensors and actuators.  
✅ Offers **abstract base classes** for structured interface implementation

---

### **3️⃣ Interfaces (`interfaces/`)**

Implements **communication interfaces** between hardware components, system utilities, and external services.

✅ Handles **configuration management, and hardware initialization**.  
✅ Provides structured **logging and system state management**.  
✅ Ensures **hardware access synchronization** to prevent conflicts.

---


### **4️⃣ Procedures (`procedures/`)**

Implements **core system functions** required for sensor operation and data collection.

✅ **Calibration procedures** for CO₂ and humidity sensor accuracy.  
✅ **Measurement routines** for CO₂, wind, and auxilliary sensor data.  
✅ **System health monitoring** to log CPU/memory usage and detect issues.

---

### **5️⃣ Utils (`utils/`)**

Provides **helper functions and system utilities** to support the main application.

✅ Implements **message queues, ring buffers, and GPIO management**.  
✅ Supports **error handling, logging, and data formatting**.  
✅ Provides **system diagnostics and execution control**.

---

## **Execution Flow**

1️⃣ **Startup**: `main.py` initializes configuration, hardware, and system state.  
2️⃣ **System Checks**: Validates hardware and system health before operation.  
3️⃣ **Calibration**: Runs calibration if scheduled.  
4️⃣ **Measurements**: Captures and processes environmental sensor data.  
5️⃣ **Logging & Communication**: Queues data for edge gateway, logs system status.  
6️⃣ **Continuous Operation**: Runs in an infinite loop, retrying failed operations.

---

## **Summary**

✅ **Modular Architecture** → Organized structure for maintainability.  
✅ **Flexible & Scalable** → Supports additional sensors and features.  
✅ **Real-Time Data Processing** → Captures, logs, and transmits sensor data.  
✅ **Resilient Operation** → Handles failures gracefully.

<br>

For further details, refer to the individual subdirectory READMEs and module documentation.
