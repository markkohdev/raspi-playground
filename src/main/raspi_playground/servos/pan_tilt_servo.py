"""
Pan and Tilt a camera with two SG90 servos using keyboard input.
W/S to tilt up/down, A/D to pan left/right.

Heavily inspired by:
https://phazertech.com/tutorials/rpi-gpio.html
"""

from sshkeyboard import listen_keyboard
import time
from adafruit_servokit import ServoKit

servos = ServoKit(channels=16)

# Calibrated SG90 Servo Ranges
# Servo 0 (Pan) = 180 degrees, 400-2680ms pulse width
# Servo 1 (Tilt) = 90 degrees, 1500-2500ms pulse width (in mounting bracket)

# Setup Pan Servo
pan_servo = servos.servo[0]
pan_servo.set_pulse_width_range(400, 2680)
pan_servo.actuation_range = 180

# Setup Tilt Servo
tilt_servo = servos.servo[1]
tilt_servo.set_pulse_width_range(1550, 2500)
tilt_servo.actuation_range = 90


# Start the pan in the middle and tilt all the way down
pan_angle = 90
tilt_angle = 0

release_a = False
release_d = False
release_w = False
release_s = False

pan_servo.angle = pan_angle
tilt_servo.angle = tilt_angle


def press(key):
    global pan_angle, tilt_angle, release_a, release_d, release_w, release_s

    if key == "w":
        release_w = False
        while tilt_angle < tilt_servo.actuation_range and not release_w:
            tilt_angle += 1
            tilt_servo.angle = tilt_angle
            time.sleep(0.01)

    elif key == "s":
        release_s = False
        while tilt_angle > 0 and not release_s:
            tilt_angle -= 1
            tilt_servo.angle = tilt_angle
            time.sleep(0.01)

    elif key == "a":
        release_a = False
        while pan_angle > 0 and not release_a:
            pan_angle -= 1
            pan_servo.angle = pan_angle
            time.sleep(0.01)

    elif key == "d":
        release_d = False
        while pan_angle < pan_servo.actuation_range and not release_d:
            pan_angle += 1
            pan_servo.angle = pan_angle
            time.sleep(0.01)

    print(f"Pan angle: {pan_angle}, Tilt angle: {tilt_angle}")


def release(key):
    global release_a, release_d, release_w, release_s

    if key == "w":
        release_w = True

    elif key == "s":
        release_s = True

    elif key == "a":
        release_a = True

    elif key == "d":
        release_d = True


def exit() -> bool:
    print("Exiting...")
    pan_servo.angle = None
    tilt_servo.angle = None
    return False  # Stop listener


print("Use W/S to tilt up/down, A/D to pan left/right. Press 'q' to quit.")

listen_keyboard(on_press=press, on_release=release, until="q", delay_second_char=0.001)

exit()
