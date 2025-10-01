import pygame, socket, time

PI_IP = "10.46.74.1"  
PI_PORT = 5007
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("❌ No controller found!")
    exit()
js = pygame.joystick.Joystick(0)
js.init()
print(f"🎮 Controller: {js.get_name()}")

def nudge_axis(val, max_step=20, deadzone=0.2):
    if abs(val) < deadzone:
        return 0
    return int(val * max_step)

# --- New servo state ---
servo3_angle = 0        # start closed
servo3_open_angle = 90
servo3_closed_angle = 0
servo3_state = False     # False = closed, True = open

last_btn = 0

while True:
    pygame.event.pump()

    # --- Tank drive with D-Pad + RT throttle ---
    hat_x, hat_y = js.get_hat(0)
    rt = js.get_axis(5)   # RT: -1 → +1
    lt = js.get_axis(4)   # LT: -1 → +1
    throttle = (rt + 1) / 2
    base_speed = 100
    speed_val = int(base_speed * throttle)

    left_speed, right_speed = 0, 0
    if hat_y == 1:   # D-Pad up → forward
        left_speed, right_speed = speed_val, speed_val
    elif hat_y == -1:  # D-Pad down → backward
        left_speed, right_speed = -speed_val, -speed_val
    elif hat_x == 1: # D-Pad left → spin left
        left_speed, right_speed = speed_val, -speed_val
    elif hat_x == -1:  # D-Pad right → spin right
        left_speed, right_speed = -speed_val, speed_val


    # --- Joysticks give scaled nudges ---
    servo2 = nudge_axis(js.get_axis(3))   
    servo1 = nudge_axis(-js.get_axis(0))    

    # --- Claw mapped to LT ---
    claw_open = int(((lt + 1) / 2) * 50)

    # --- Toggle for servo3 with A button ---
    btn = js.get_button(0)  # A button
    if btn and not last_btn:  # just pressed
        servo3_state = not servo3_state
        servo3_angle = servo3_open_angle if servo3_state else servo3_closed_angle
    last_btn = btn

    # --- Send full message ---
    msg = f"{left_speed},{right_speed},{servo1},{servo2},{servo3_angle},{claw_open}"
    sock.sendto(msg.encode(), (PI_IP, PI_PORT))
    print("➡️", msg)

    time.sleep(0.05)  # ~20 updates/sec
