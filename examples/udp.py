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
servos = [0, 4]   # 0=claw, 4=arm
angles  = {ch: 0 for ch in servos}
targets = angles.copy()
speeds  = {0: 5, 4: 5}
ALIVE = True

def servo_update(ch, ang):
    set_servo_angle(ch, ang)
    angles[ch] = ang  

def servo_worker(ch, hz=60):
    period = 1.0 / hz
    while ALIVE:
        cur, tgt = angles[ch], targets[ch]
        if cur != tgt:
            diff = tgt - cur
            step = max(1, abs(diff) // speeds[ch])
            cur += step if diff > 0 else -step
            servo_update(ch, cur)
        time.sleep(period)

for ch in servos:
    threading.Thread(target=servo_worker, args=(ch,), daemon=True).start()

def set_targets(batch):
    for ch, ang in batch.items():
        ang = max(0, min(180, int(round(ang))))
        targets[ch] = ang

def kill():
    global ALIVE
    ALIVE = False
    print("🔻 Releasing servos...")
    for ch in servos:
        pwm.setServoPulse(ch, 0)

servo_map = {'1': 0, '2': 4}  # claw=0, arm=4

try:
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            # Expect: "left,right,claw,servo2"
            parts = data.decode().strip().split(",")
            left_spd  = int(parts[0])
            right_spd = int(parts[1])
            s1 = int(parts[2])   # claw
            s2 = int(parts[3])   # arm

            # --- Send signed speeds to Nano ---
            ser.write(f"{left_spd},{right_spd}\n".encode())

            # --- Update servos ---
            set_targets({
                servo_map['1']: s1,   # claw
                servo_map['2']: s2,   # arm
            })

            print(f"Left={left_spd} Right={right_spd} | Claw={s1} Arm={s2}")

        except Exception as e:
            print("Parse error:", e)

except KeyboardInterrupt:
    kill()
    ser.close()
    sock.close()
    print("👋 Exiting cleanly")
