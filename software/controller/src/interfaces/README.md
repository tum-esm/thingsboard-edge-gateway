# Interfaces

This directory provides structured interfaces for hardware control, configuration management, state persistence, and logging, ensuring modular and maintainable system architecture.

## Directory Structure

```bash
📁 interfaces
    📄 communication_queue.py   # Interface for talking to the gateway
    📄 config_interface.py      # Interface for handling configuration file
    📄 state_interface.py       # Interface for managing system state
    📄 logging_interface.py     # Interface for structured logging and MQTT support
    📄 hardware_interface.py    # Wrapper for hardware interactions
```

## Interface Descriptions

### **Configuration Interface (`config_interface.py`)**

- Initialises the connection to the communication queue SQLite DB
- Enqueues MQTT messages to the gateway to be forwarded to Thingsboard
- Enqueues healt check messages for the gateway

### **Configuration Interface (`config_interface.py`)**

- Reads and validates configuration file
- Uses Pydantic for runtime schema validation for `config/config.json`
- Raises `FileIsMissing` and `FileIsInvalid` exceptions

### **State Interface (`state_interface.py`)**

- Ensures state file existence and integrity
- Uses Pydantic for runtime schema validation for `config/state.json`
- Persists system state across restarts

### **Logging Interface (`logging_interface.py`)**

- Implements hierarchical logging with different verbosity levels
- Supports MQTT-based remote logging for real-time monitoring
- Provides utilities for structured log formatting

### **Hardware Interface (`hardware_interface.py`)**

- Implements structured initialization and teardown of hardware components
- Provides device interactions through a centralized interface
- Provides `HwLock` to prevent simultaneous hardware access
- Raises `HardwareOccupiedError` when a resource conflict is detected

<br>

---

For further details on specific implementations, refer to the respective module documentation.
