import os
import time
import cv2

import threading
import signal
import sys
from collections import deque

from flask import Flask, render_template, request, redirect, send_file, url_for, Response, jsonify, flash
from ultralytics import YOLO
import torch

from functions import login, screenshot, clip_video, log, create_timelapse, upload_source, fetch_media, fetch_logs, zoom, login

app = Flask(__name__)
app.secret_key = os.urandom(24)

frameBuffer = deque(maxlen=300)
frameLock = threading.Lock()
showYolo = False 
zoomFactor = 1

#Load the YOLO model
modelPath = "AI Models"
model = YOLO(f"{modelPath}\yolov8n.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

currentFrame = None

def capture_frame():
    global currentFrame
    camera = cv2.VideoCapture(0)

    try:
        while True:
            success, frame = camera.read()
            global showYolo
            global zoomFactor
            if not success:
                break
            with frameLock:
                if showYolo:
                    frame = apply_yolo(frame)
                if zoomFactor != 1:
                    frame = zoom(zoomFactor, frame, camera.get(cv2.CAP_PROP_FRAME_WIDTH), camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                currentFrame = frame
                frameBuffer.append(frame)
    finally:
        camera.release()

def generate_frames():
    for frame in capture_frame():
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        #Convert to web standard
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def apply_yolo(frame):
    #Object detection
    results = model.track(frame, classes=0, conf=0.8, imgsz=480, device=device)
    
    # Annotate frame with detection results
    annotated_frame = results[0].plot()
    cv2.putText(annotated_frame, f"Total: {len(results[0].boxes)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    
    return annotated_frame

@app.route('/toggle_yolo', methods=['POST'])
def toggle_yolo():
    global showYolo
    showYolo = not showYolo
    return jsonify({"status": "success", "showYolo": showYolo})

@app.route('/')
def index():
    return render_template('login.html')
    #Fetch recent screenshots and clips
    recentScreenshots = fetch_media('screenshots',"images")
    recentClips = fetch_media('clips',"videos")
    logs = fetch_logs()


    return render_template('index.html', 
                            recentScreenshots=recentScreenshots, 
                            recentClips=recentClips,
                        logs = logs)


@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Pass email and password to external login_manager file
        success, e = login(email, password)

        if success:
            flash('Login successful', 'success')
            print("SUIII")  # Redirect to dashboard after login
        elif e:
            flash(f"An error occurred: {str(e)}", 'danger')
        else:
            flash(f'Login failed. Please check your credentials and try again.', 'danger')
    return render_template('login.html')

@app.route('/video_feed')
 

@app.route('/take_screenshot', methods=['POST'])
def take_screenshot():
    with frameLock:
        if not frameBuffer:
            return jsonify({"status": "error", "message": "No frame available"}), 400
        frame = frameBuffer[-1]
    
    metadata = {"Time": time.strftime("%Y-%m-%d %H:%M:%S"), 
                "Location": "N/A", 
                "Reason": "User", 
                "Resolution": "1920x1080", 
                "NUM": 2}
    _, encoded_image = cv2.imencode('.jpg', frame)

    screenshot(encoded_image, "screenshots", "screenshot", metadata)

    return jsonify({"status": "screenshot taken"})

@app.route('/record_clip', methods=['POST'])
def record_clip():
    metadata = {"Time": time.strftime("%Y-%m-%d %H:%M:%S"), 
                "Location": "N/A", 
                "Reason": "User", 
                "Resolution": "1920x1080", 
                "NUM": 2}

    clip_video(frameBuffer, 24, 2, "clips", "clip", metadata)

    return jsonify({"status": "clip record"})

@app.route('/set_zoom', methods=['POST'])
def set_zoom():
    global zoomFactor
    data = request.get_json() 
    zoomFactor = float(data.get('zoom', 1.0))

    return jsonify({"message": "Zoom value updated", "zoom": zoomFactor})


if __name__ == '__main__':
    """
    t = threading.Thread(target=capture_frame)
    t.daemon = True
    t.start()
    """
    
    app.run(host='0.0.0.0', port=5000) #threaded=True)



