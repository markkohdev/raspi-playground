from gpiozero import LED, Button, Buzzer
from time import sleep
from signal import pause

button = Button(2)
buzzer = Buzzer(17)

button.when_pressed = buzzer.on

button.when_released = buzzer.off

pause()
