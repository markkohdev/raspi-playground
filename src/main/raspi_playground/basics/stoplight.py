from gpiozero import LED, Button, Buzzer, TrafficLights
from time import sleep
from signal import pause

# red = LED(5)
# yellow = LED(6)
# green = LED(13)
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
