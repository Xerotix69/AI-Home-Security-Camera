import os
from collections import deque
from flask import Flask, render_template, request, redirect, send_file, url_for, Response, jsonify
import cv2
import threading
import signal
import sys
import time

from functions import screenshot, create_info, upload_img, upload_vid, create_timelapse, clip_video, get_images

app = Flask(__name__)

frame_buffer = deque(maxlen=300)
frame_lock = threading.Lock()

def capture_frame():
    camera = cv2.VideoCapture(0)  # Capture video from the first webcam
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            with frame_lock:
                frame_buffer.append(frame)
            yield frame
    finally:
        camera.release()

def generate_frames():
    for frame in capture_frame():
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/images')
def get_image():
    get_images(request.args.get('path', 'screenshots'))

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_screenshot', methods=['POST'])
def take_screenshot():
    with frame_lock:
        if not frame_buffer:
            return jsonify({"status": "error", "message": "No frame available"}), 400
        frame = frame_buffer[-1]
    
    metadata = create_info(time.strftime("%Y-%m-%d %H:%M:%S"), "N/A", "User", "1920x1080", 2)

    screenshot(frame, "screenshots", "screenshot", metadata)

    return jsonify({"status": "screenshot taken"})

if __name__ == '__main__':
    app.run(debug=True)
