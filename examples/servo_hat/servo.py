from driver_servo import *
import time

s = 15  # servo channel

while True:
    set_servo_angle(s, 0)
    time.sleep(1)
    set_servo_angle(s, 180)
    time.sleep(1)   # <- missing delay
