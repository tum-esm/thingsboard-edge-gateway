import time
from simple_pid import PID

from utils.read_temperature import read_sensor_temperature
from utils.set_ventilator import set_venitlation_on, set_venitlation_off
from utils.set_heater import set_heater_pwm
  
# Define the simulated system (the plant)
class HeaterSystem:
    def __init__(self):
        self.temperature = read_sensor_temperature() 

    def update(self, control_signal):
        """
        Updates the pwm duty cycle based on the temperature.
        A larger control signal (more power) increases the temperature more quickly.
        """
        # Simple model: increase temperature proportional to control signal
        set_heater_pwm(control_signal)
        self.temperature = read_sensor_temperature()
        
        return self.temperature

# Initialize the system
system = HeaterSystem()

# Create PID controller with desired gains
pid = PID(1, 0.1, 0.05, setpoint=40)
pid.output_limits = (0, 1) 

temp = system.update(0)

try: 
    set_venitlation_on()
    print_frequency = time.time()
    
    while True:
        # Compute new output from the PID according to the systems current temp
        control = pid(temp)
        #print(control)

        # Feed the PID output to the system and get its current value
        temp = system.update(control)
        
        time.sleep(0.1)
         
        if time.time() - print_frequency > 5:
            print_frequency = time.time()
            print("Box Temperature: ",round(system.temperature, 2))
            print("PWM Duty Cycle:   ", round(control,2))
finally:
    print("powering of pins")
    set_heater_pwm(0)
    set_venitlation_off()
