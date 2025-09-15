import serial
import sys
import termios
import tty
import time
import select

# --- Serial setup ---
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # give Nano time to reset

# --- Setup terminal ---
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
tty.setcbreak(fd)

print("Keyboard control ready! Hold keys to drive:")
print("W = Forward | S = Backward | A = Left | D = Right | Q = Quit")

try:
    while True:
        # Check if a key is pressed (non-blocking)
        dr, dw, de = select.select([sys.stdin], [], [], 0.05)

        if dr:
            key = sys.stdin.read(1).lower()

            if key == 'w':
                ser.write(b'F')
                print("Forward")
            elif key == 's':
                ser.write(b'B')
                print("Backward")
            elif key == 'a':
                ser.write(b'L')
                print("Left")
            elif key == 'd':
                ser.write(b'R')
                print("Right")
            elif key == 'q':
                ser.write(b'S')
                print("Exiting…")
                break
        else:
            # No key pressed → stop motors
            ser.write(b'S')
            # (comment out the next line if you don’t want spam)
            # print("Stop")

except KeyboardInterrupt:
    ser.write(b'S')

finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    ser.close()
    print("Serial closed")
