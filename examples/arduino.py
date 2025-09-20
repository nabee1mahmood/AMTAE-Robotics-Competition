import pygame
import serial
import time
import sys

# --- Serial setup ---
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # give Nano time to reset

# --- Pygame setup ---
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ No controller found!")
    sys.exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Using controller: {joystick.get_name()}")

print("Controls ready! Use Left Stick or D-Pad | Press B to quit")

running = True
while running:
    pygame.event.pump()

    # Left Stick axes
    x_axis = joystick.get_axis(0)  # left/right
    y_axis = joystick.get_axis(1)  # forward/backward

    # D-Pad (hat switch)
    hat_x, hat_y = joystick.get_hat(0)

    # Button mapping (example: Xbox controller: B = 1)
    b_button = joystick.get_button(1)

    cmd = None

    # Analog stick control
    if y_axis < -0.5:      # Forward
        cmd = b'F'
        print("Forward")
    elif y_axis > 0.5:     # Backward
        cmd = b'B'
        print("Backward")
    elif x_axis < -0.5:    # Left
        cmd = b'L'
        print("Left")
    elif x_axis > 0.5:     # Right
        cmd = b'R'
        print("Right")

    # D-Pad override (digital)
    elif hat_y == 1:
        cmd = b'F'
        print("Forward (D-pad)")
    elif hat_y == -1:
        cmd = b'B'
        print("Backward (D-pad)")
    elif hat_x == -1:
        cmd = b'L'
        print("Left (D-pad)")
    elif hat_x == 1:
        cmd = b'R'
        print("Right (D-pad)")

    # Stop if no input
    else:
        cmd = b'S'

    # Quit button
    if b_button:
        print("👋 Exiting…")
        ser.write(b'S')
        running = False

    # Send command to Arduino
    if cmd:
        ser.write(cmd)

    time.sleep(0.05)  # 20 Hz update

# Cleanup
ser.close()
pygame.quit()
print("Serial closed, pygame quit.")
