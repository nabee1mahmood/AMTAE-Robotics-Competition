#!/usr/bin/python3
from flask import Flask, request
from PCA9685 import PCA9685

# ----- Motor Driver -----
class MotorDriver():
    def __init__(self, pwm):
        self.pwm = pwm
        self.PWMA = 0; self.AIN1 = 1; self.AIN2 = 2
        self.PWMB = 5; self.BIN1 = 3; self.BIN2 = 4

    def run(self, motor, direction, speed=100):
        if speed > 100: 
            return
        if motor == 0:  # Left
            self.pwm.setDutycycle(self.PWMA, speed)
            if direction == "forward":
                self.pwm.setLevel(self.AIN1, 0)
                self.pwm.setLevel(self.AIN2, 1)
            else:
                self.pwm.setLevel(self.AIN1, 1)
                self.pwm.setLevel(self.AIN2, 0)
        else:  # Right
            self.pwm.setDutycycle(self.PWMB, speed)
            if direction == "forward":
                self.pwm.setLevel(self.BIN1, 0)
                self.pwm.setLevel(self.BIN2, 1)
            else:
                self.pwm.setLevel(self.BIN1, 1)
                self.pwm.setLevel(self.BIN2, 0)

    def stop(self, motor):
        self.pwm.setDutycycle(self.PWMA if motor == 0 else self.PWMB, 0)


# Init motor
motor_pwm = PCA9685(0x40, debug=False)
motor_pwm.setPWMFreq(1000)
Motor = MotorDriver(motor_pwm)

def stop_all():
    Motor.stop(0); Motor.stop(1)


# ----- Flask App -----
app = Flask(__name__)

@app.route("/cmd")
def command():
    cmd = request.args.get("c")
    if not cmd:
        return "No command"

    if cmd == "x":  # stop all
        stop_all()
        return "Stopped"

    # Left tread command: lt{speed}{dir}
    if cmd.startswith("lt"):
        speed = int(cmd[2:-1])
        direction = "forward" if cmd[-1] == "f" else "backward"
        Motor.run(0, direction, speed)
        return f"Left {direction} {speed}"

    # Right tread command: rt{speed}{dir}
    if cmd.startswith("rt"):
        speed = int(cmd[2:-1])
        direction = "forward" if cmd[-1] == "f" else "backward"
        Motor.run(1, direction, speed)
        return f"Right {direction} {speed}"

    return "Unknown command"


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080)
    finally:
        stop_all()
