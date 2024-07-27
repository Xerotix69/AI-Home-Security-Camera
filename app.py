import os
import pickle
import numpy as np

from flask import Flask, request, render_template, Response
import cv2

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

capture = cv2.VideoCapture(0)
capture.set(3, 640)
capture.set(4, 480)

@app.route('/video_feed')
def video_feed():
    # Return the response generated along with the specific media type (mime type)
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Render the index.html template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

