import socket, serial, time
from driver_servo import set_servo_angle, pwm

# --- Serial for Nano motors ---
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# --- UDP setup ---
UDP_IP = "0.0.0.0"
UDP_PORT = 5007
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"📡 Listening on {UDP_PORT}...")

# --- Servo channels ---
claw_servo, servo_a, servo_b = 12, 13, 14
servos = [servo_a, servo_b, claw_servo]

# Current angles
angles = {ch: 90 for ch in servos}   # start centered

# Per-servo speed multipliers (smaller = slower movement)
servo_speed = {
    servo_a: 0.3,     # 30% of incoming step
    servo_b: 0.5,     # 50% of incoming step
    claw_servo: 1.0   # full speed for claw
}

def clamp(val, lo=0, hi=180):
    return max(lo, min(hi, val))

try:
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            # Expect: left,right,s1,s2,claw
            left_spd, right_spd, s1, s2, claw = map(int, data.decode().strip().split(","))

            # --- Drive motors ---
            ser.write(f"{left_spd},{right_spd}\n".encode())

            # --- Apply scaled servo deltas ---
            angles[servo_a] = clamp(angles[servo_a] + int(s1 * servo_speed[servo_a]))
            angles[servo_b] = clamp(angles[servo_b] + int(s2 * servo_speed[servo_b]))
            angles[claw_servo] = clamp(int(claw * servo_speed[claw_servo]))  # absolute

            # Send to hardware
            for ch in servos:
                set_servo_angle(ch, angles[ch])

            print(f"Motors: L={left_spd} R={right_spd} | "
                  f"S1={angles[servo_a]} S2={angles[servo_b]} Claw={angles[claw_servo]}")

        except Exception as e:
            print("Parse error:", e, "raw:", data)

except KeyboardInterrupt:
    print("👋 Exiting...")
    ser.close()
    sock.close()
    for ch in servos:
        pwm.setServoPulse(ch, 0)
