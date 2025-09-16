from gpiozero import LightSensor
from time import sleep

"""
Pinout:
    - LightSensor: GPIO 5

LightSensor: 
    - 3v -> light sensor leg 1
    - GPIO -> light sensor leg 2 / capacitor -> ground
"""
ldr = LightSensor(27)

while True:
    print("Light Level:", ldr.value)
    # sleep(1)
