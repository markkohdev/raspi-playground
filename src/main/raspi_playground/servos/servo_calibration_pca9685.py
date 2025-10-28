"""
Servo Calibration Script for PCA9685 Controller

This script helps calibrate the pulse width range and actuation range (physical range of motion in degrees) of multiple servo motors connected to a PCA9685 controller.

Current Logic:
1. User selects the servo channel to calibrate.
2. User enters the actuation range in degrees (e.g., 90 for pan-tilt mounts, default 180).
3. User enters the minimum and maximum pulse widths in microseconds (defaults provided).
4. User sets the servo angle, restricted to [0, actuation_range].
5. The script sets the pulse width range and angle for the servo, enforcing the actuation range limit.
6. User can repeat calibration for the same or another servo channel, or exit.

This allows calibration of servos with limited physical movement and ensures angle input matches the configured actuation range.
"""

from adafruit_servokit import ServoKit

servos = ServoKit(channels=16)


def get_int_input(prompt, default):
    value = input(prompt)
    if value.strip() == "":
        return default
    return int(value)


def calibrate_servo(channel):
    my_servo = servos.servo[channel]
    min_pulse = 1000
    max_pulse = 2000
    default_actuation_range = 180
    actuation_range_input = input(
        f"Enter the actuation range in degrees (default {default_actuation_range}, or 'exit' to finish): "
    )
    if actuation_range_input.lower() == "exit":
        my_servo.angle = None
        return
    actuation_range = int(actuation_range_input) if actuation_range_input.strip() != "" else default_actuation_range
    my_servo.actuation_range = actuation_range
    last_angle = actuation_range // 2
    while True:
        min_input = input(f"Enter the minimum pulse width in microseconds (default {min_pulse}, or 'exit' to finish): ")
        if min_input.lower() == "exit":
            my_servo.angle = None
            break
        min_pulse = int(min_input) if min_input.strip() != "" else min_pulse

        max_input = input(f"Enter the maximum pulse width in microseconds (default {max_pulse}, or 'exit' to finish): ")
        if max_input.lower() == "exit":
            my_servo.angle = None
            break
        max_pulse = int(max_input) if max_input.strip() != "" else max_pulse

        angle_input = input(
            f"Enter the angle to set the servo to (0-{actuation_range}, default {last_angle}, or 'exit' to finish): "
        )
        if angle_input.lower() == "exit":
            my_servo.angle = None
            break
        angle = int(angle_input) if angle_input.strip() != "" else last_angle
        if 0 <= angle <= actuation_range:
            my_servo.set_pulse_width_range(min_pulse, max_pulse)
            my_servo.angle = angle
            last_angle = angle
            print(f"Set pulse width range to {min_pulse}-{max_pulse} microseconds.")
            print(f"Set servo to {angle} degrees (actuation range: {actuation_range}).")
        else:
            print(f"Angle must be between 0 and {actuation_range} degrees.")

    print(f"Final pulse width range for channel {channel}: {min_pulse}-{max_pulse} microseconds.")


def main():
    while True:
        try:
            channel_input = input("Enter the servo channel number (0-15) to calibrate or 'exit' to finish: ")
            if channel_input.lower() == "exit":
                break
            channel = int(channel_input)
            if 0 <= channel <= 15:
                calibrate_servo(channel)
            else:
                print("Channel must be between 0 and 15.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")
            continue
        another = input("Do you want to calibrate another servo? (y/n): ").lower()
        if another != "y":
            break
    print("Calibration complete.")


if __name__ == "__main__":
    main()
