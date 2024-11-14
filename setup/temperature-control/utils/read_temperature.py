import smbus2

bus = smbus2.SMBus(1)
adress = 0x18
register = 0x05

def read_sensor_temperature():
    # read sensor
    result = bus.read_word_data(adress, register)

    # swap the bytes
    data = (result & 0xff) << 8 | (result & 0xff00) >> 8
    if data & 0x1000:
        data = -((data ^ 0x0FFF) + 1)
    else:
        data = data & 0x0fff
    return data / 16.0

if __name__ == "__main__":
    print(read_sensor_temperature())