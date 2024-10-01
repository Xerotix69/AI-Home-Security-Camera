import cv2
from flask import Blueprint, render_template, Response
from stream import get_frames
import time

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return render_template('dashboard.html')

@main_routes.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main_routes.route('/video_feed')
def video_feed():
    print("Asda")
    get_frames(1)
    print("FSAFASF")
    return render_template('dashboard.html')
    """
    def generate_frames():
        while True:
            print("d")
            frame = get_frames(1)
            if frame is None:
                print("No frame available")
                continue
            try:
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    print("Failed to encode frame")
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                print(f"Error in generate_frames: {str(e)}")
                continue

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    """