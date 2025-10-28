import time
from gpiozero import Button, OutputDevice
from signal import pause

# --- Configuration ---

# 1. The pump is connected to the relay, which is controlled by GPIO 12.
#    We use 'OutputDevice' because the relay isn't just an LED.
#    'active_high=True' means HIGH (3.3V) turns it ON, LOW (0V) turns it OFF.
pump_relay = OutputDevice(12, active_high=True, initial_value=False)

# 2. The button is connected to GPIO 27.
#    'pull_down=True' enables the Pi's internal pull-down resistor.
#    This means the pin reads LOW until the button is pressed,
#    which connects it to 3.3V and makes it read HIGH.
spray_button = Button(27)

# --- Logic ---

print("Counter Intelligence system armed.")
print("Press the button to test the sprayer...")


def spray_on():
    """Called when the button is pressed."""
    print("Button Pressed: Firing sprayer!")
    pump_relay.on()


def spray_off():
    """Called when the button is released."""
    print("Button Released: Stopping sprayer.")
    pump_relay.off()


# Link the button events to the functions
spray_button.when_pressed = spray_on
spray_button.when_released = spray_off


# The 'pause()' function keeps the script running in the background
# to listen for button presses.
try:
    pause()

except KeyboardInterrupt:
    print("Shutting down...")
    pump_relay.off()
