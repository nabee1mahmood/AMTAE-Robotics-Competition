#!/usr/bin/python

from PCA9685 import PCA9685
import time

motor_pwm = PCA9685(0x40, debug=False)
motor_pwm.setPWMFreq(1000)  # faster for DC motors

class MotorDriver():
    def __init__(self, pwm):
        self.pwm = pwm
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

    def MotorRun(self, motor, index, speed):
        if speed > 100:
            return
        if motor == 0:  # Motor A
            self.pwm.setDutycycle(self.PWMA, speed)
            if index == 'forward':
                self.pwm.setLevel(self.AIN1, 0)
                self.pwm.setLevel(self.AIN2, 1)
            else:
                self.pwm.setLevel(self.AIN1, 1)
                self.pwm.setLevel(self.AIN2, 0)
        else:  # Motor B
            self.pwm.setDutycycle(self.PWMB, speed)
            if index == 'forward':
                self.pwm.setLevel(self.BIN1, 0)
                self.pwm.setLevel(self.BIN2, 1)
            else:
                self.pwm.setLevel(self.BIN1, 1)
                self.pwm.setLevel(self.BIN2, 0)

    def MotorStop(self, motor):
        if motor == 0:
            self.pwm.setDutycycle(self.PWMA, 0)
        else:
            self.pwm.setDutycycle(self.PWMB, 0)

# ----------------- DEMO -----------------
Motor = MotorDriver(motor_pwm)

print("Run motors forward")
Motor.MotorRun(0, 'forward', 80)
Motor.MotorRun(1, 'forward', 80)

time.sleep(1)   

print("Stop motors")
Motor.MotorStop(0)
Motor.MotorStop(1)
