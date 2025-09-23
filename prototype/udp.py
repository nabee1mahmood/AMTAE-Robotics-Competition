import socket, serial, threading, time
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
servo_a, servo_b, servo_c, servo_d = 12, 13, 14, 15
servos = [servo_a, servo_b, servo_c, servo_d]

# Current + target angles
angles  = {ch: 90 for ch in servos}   # start centered
targets = angles.copy()
speeds  = {
    servo_a: 3,
    servo_b: 5,
    servo_c: 7,
    servo_d: 1
}
ALIVE = True

servo_map = {'1': servo_a, '2': servo_b, '3': servo_c, '4': servo_d}

def servo_update(ch, ang):
    set_servo_angle(ch, ang)
    angles[ch] = ang

def servo_worker(ch, hz=60, start_delay=0):
    time.sleep(start_delay)   # 🔹 staggered startup
    period = 1.0 / hz
    while ALIVE:
        cur, tgt = angles[ch], targets[ch]
        if cur != tgt:
            diff = tgt - cur
            step = max(1, abs(diff) // speeds[ch])
            cur += step if diff > 0 else -step
            servo_update(ch, cur)
        time.sleep(period)

def kill():
    global ALIVE
    ALIVE = False
    print("🔻 Releasing servos...")
    for ch in servos:
        pwm.setServoPulse(ch, 0)

# --- Stagger servo threads ---
startup_delay = 3  # wait 3 sec after boot
print(f"⏳ Waiting {startup_delay}s before engaging servos...")
time.sleep(startup_delay)

for i, ch in enumerate(servos):
    threading.Thread(
        target=servo_worker,
        args=(ch, 60, i),   # stagger each servo by 1s
        daemon=True
    ).start()

try:
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            left_spd, right_spd, s1, s2, s3, s4 = map(int, data.decode().strip().split(","))

            # --- Drive motors (send signed speeds to Nano) ---
            ser.write(f"{left_spd},{right_spd}\n".encode())

            # --- Apply servo nudges (deltas) ---
            steps = {
                servo_map['1']: s1,
                servo_map['2']: s2,
                servo_map['3']: s3,
                servo_map['4']: s4,
            }
            for ch, delta in steps.items():
                new_ang = max(0, min(180, angles[ch] + delta))
                targets[ch] = new_ang

            print(f"Left={left_spd} Right={right_spd} | "
                  f"S1={angles[servo_a]} S2={angles[servo_b]} "
                  f"S3={angles[servo_c]} S4={angles[servo_d]}")

        except Exception as e:
            print("Parse error:", e)

except KeyboardInterrupt:
    kill()
    ser.close()
    sock.close()
    print("👋 Exiting cleanly")


