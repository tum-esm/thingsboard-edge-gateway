# Utils

The `utils` directory contains various utility modules that provide supporting functionalities for the main system, including data processing, hardware interaction, error handling, and system management.

## Directory Structure

```bash
📁 utils
    📄 alarms.py                      # Handles system alarms and timeout management
    📄 athmospheric_conversion.py     # Provides conversion functions for atmospheric parameters
    📄 expontential_backoff.py        # Implements exponential backoff for error handling
    📄 extract_true_bottle_value.py   # Extracts true values from cylinder measurement log
    📄 gpio_pin_factory.py            # Manages GPIO pin access to avoid conflicts
    📄 list_operations.py             # Utility functions for handling lists
    📄 message_queue.py               # Implements a message queue to communicate with edge gateway
    📄 paths.py                       # Defines standard paths used in the system
    📄 ring_buffer.py                 # Implements a ring buffer for sensor data storage
    📄 system_info.py                 # Retrieves system information such as CPU usage, memory, and uptime
```
