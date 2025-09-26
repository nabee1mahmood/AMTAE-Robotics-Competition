import cv2
import numpy as np
from picamera2 import Picamera2

# Init camera
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

while True:
    frame = picam2.capture_array()
    
    
    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Competiton colors: Red, Green, Blue, Yellow
    
    # detect blue ball
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([0, 0, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # detect green ball
    lower_green = np.array([40, 70, 70])
    upper_green = np.array([0, 255, 0])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # detect yellow ball
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([0, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # detect red ball
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([255, 0, 0])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # Here you would send commands to motors to pick up the ball

    cv2.imshow("Ball Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break