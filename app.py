import os

from flask import Flask, render_template, request, redirect, send_file, url_for, Response
import cv2

from ultralytics import YOLO

app = Flask(__name__)

def generate_frames():
    camera = cv2.VideoCapture(0)  # Capture video from the first webcam
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

if __name__ == '__main__':
    app.run(debug=True)