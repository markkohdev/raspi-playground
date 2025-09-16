from gpiozero import Button, Buzzer, TrafficLights
from time import sleep

"""
Pinout:
    - Red: GPIO 5
    - Yellow: GPIO 6
    - Green: GPIO 13
    - Buzzer: GPIO 17
    - Button: GPIO 27

Lights: GPIO -> resistor -> led -> ground
Buzzer: GPIO -> buzzer -> ground
Button: GPIO -> button -> ground
"""
lights = TrafficLights(5, 6, 13)

buzzer = Buzzer(17)
button = Button(27)

button.when_pressed = buzzer.on

button.when_released = buzzer.off

while True:
    button.wait_for_press()
    lights.red.on()
    sleep(10)
    lights.red.off()
    lights.yellow.on()
    sleep(1)
    lights.yellow.off()
    lights.green.on()
    i = 0
    while i < 5:
        buzzer.on()
        sleep(0.1)
        buzzer.off()
        sleep(0.250)
        i += 1
    lights.green.off()
    lights.off()
