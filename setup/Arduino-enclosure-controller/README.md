# Arduino Enclosure Controller Setup

This directory contains the firmware and setup instructions for the Arduino-based enclosure controller, which manages environmental conditions within the sensor enclosure.

## File Structure

```bash
📁 /enclosure_controller/
    📄 enclosure_controller.ino  # Main firmware file
    📄 config.h                  # Configuration file
    📄 platformio.ini            # PlatformIO configuration file
```

## Requirements

- **Arduino Board** (e.g., Arduino Uno, Mega, or compatible)
- **Sensors & Actuators**:
  - **DS18B20 Temperature Sensor** (requires a **4.7kΩ pull-up resistor** on the data pin)
  - **Enclosure Heater** (connected to **pin 3**)
  - **Enclosure Fan** (connected to **pin 4**)
- **Arduino IDE** or PlatformIO for compilation and upload

## Dependencies

This project requires the following external libraries:

- **OneWire** (version 2.3.7) – Used for communication with DS18B20
- **DallasTemperature** (version 3.9.0) – Simplifies temperature reading from DS18B20

### **Installing Dependencies**

For **Arduino IDE**, install via the Library Manager:

1. Open Arduino IDE.
2. Navigate to **Sketch** → **Include Library** → **Manage Libraries**.
3. Search for "OneWire" and install version **2.3.7**.
4. Search for "DallasTemperature" and install version **3.9.0**.

For **PlatformIO**, dependencies are managed automatically via `platformio.ini`. No manual installation is required.

## Setup Instructions

1. **Connect the hardware**:

   - **DS18B20 Temperature Sensor**:
     - Data pin → **Arduino digital pin 2**
     - Requires a **4.7kΩ pull-up resistor** between VCC and Data
   - **Enclosure Heater**: Connect to **pin 3**
   - **Enclosure Fan**: Connect to **pin 4**

2. **For Arduino IDE Users**:

   - Open `enclosure_controller.ino` in the Arduino IDE.
   - Select the correct board and port from `Tools > Board` and `Tools > Port`.
   - Ensure dependencies are installed (see above section).
   - Upload the firmware to the Arduino board.

3. **For PlatformIO Users**:

   - Ensure `platformio.ini` is correctly configured.
   - Run the following command to build and upload:
     ```bash
     pio run --target upload
     ```
   - Open the serial monitor with:
     ```bash
     pio device monitor
     ```

4. **Verify operation**:
   - Open the **Serial Monitor** (`9600 baud` for Arduino IDE, `pio device monitor` for PlatformIO).
   - Observe temperature readings and relay state changes.

## Control Logic

- Reads **temperature** from DS18B20.
- **Turns on the heater** when the temperature falls below `TARGET_TEMPERATURE - ALLOWED_TEMPERATURE_DEVIATION`.
- **Turns off the heater** once `TARGET_TEMPERATURE` is reached.
- **Turns on the fan** if temperature exceeds `TARGET_TEMPERATURE + ALLOWED_TEMPERATURE_DEVIATION`.
- **Turns off the fan** once temperature drops below `TARGET_TEMPERATURE`.
- Uses **active-low relay logic**:
  - `LOW` = Relay **ON**
  - `HIGH` = Relay **OFF**

## Usage

- The controller automatically regulates the enclosure environment.
- Logs sensor data via serial output.
- Adjusts heating and ventilation based on temperature thresholds.

<br>

---

For further details, refer to the firmware comments and external documentation if available.
