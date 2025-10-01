import socket, serial, time, glob
from driver_servo import set_servo_angle, pwm

# --- Find and connect to Nano ---
def connect_serial(baud=9600):
    while True:
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        if not ports:
            print("⏳ Waiting for Nano...")
            time.sleep(1)
            continue
        try:
            ser = serial.Serial(ports[0], baud, timeout=1)
            print(f"🔌 Connected to {ports[0]}")
            return ser
        except Exception as e:
            print("⚠️ Serial open failed:", e)
            time.sleep(1)

ser = connect_serial()

# --- UDP setup ---
UDP_IP = "0.0.0.0"
UDP_PORT = 5007
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"📡 Listening on {UDP_PORT}...")

# --- Servo channels ---
claw_servo, servo_a, servo_b, servo_c = 14, 12, 13, 11
servos = [servo_a, servo_b, servo_c, claw_servo]

# Current angles
angles = {ch: 90 for ch in servos}   # start centered

# Per-servo speed multipliers (only for delta-type)
servo_speed = {
    servo_a: 0.4,
    servo_b: 0.4,
    claw_servo: .5
}

def clamp(val, lo=0, hi=180):
    return max(lo, min(hi, val))

try:
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            # Expect: left,right,s1,s2,s3,claw
            left_spd, right_spd, s1, s2, s3, claw = map(int, data.decode().strip().split(","))

            # --- Drive motors (with auto-reconnect) ---
            try:
                ser.write(f"{left_spd},{right_spd}\n".encode())
            except Exception as e:
                print("⚠️ Serial lost, reconnecting...", e)
                ser.close()
                ser = connect_serial()

            # --- Apply scaled servo deltas (s1,s2) ---
            angles[servo_a] = clamp(angles[servo_a] + int(s1 * servo_speed[servo_a]))
            angles[servo_b] = clamp(angles[servo_b] + int(s2 * servo_speed[servo_b]))

            # --- Absolute control for servo_c and claw ---
            angles[servo_c] = clamp(s3)  
            angles[claw_servo] = clamp(claw)

            # Send to hardware
            for ch in servos:
                set_servo_angle(ch, angles[ch])

            print(f"Motors: L={left_spd} R={right_spd} | "
                  f"S1={angles[servo_a]} S2={angles[servo_b]} "
                  f"S3={angles[servo_c]} Claw={angles[claw_servo]}")

        except Exception as e:
            print("Parse error:", e, "raw:", data)

except KeyboardInterrupt:
    print("👋 Exiting...")
    try: ser.close()
    except: pass
    sock.close()
    for ch in servos:
        pwm.setServoPulse(ch, 0)
