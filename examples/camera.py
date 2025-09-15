#!/usr/bin/python3
from flask import Flask, Response
import cv2
from picamera2 import Picamera2

app = Flask(__name__)

# Init camera
picam2 = Picamera2()
# Use full sensor resolution to get full FOV
config = picam2.create_video_configuration(
    main={"size": (3280, 2464)}  # full IMX219 sensor
)
picam2.configure(config)
picam2.start()

def gen_frames():
    while True:
        frame = picam2.capture_array()
        # Downscale for streaming (small image but wide FOV)
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<img src="/video" width="640" style="transform: rotate(180deg);"/>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
