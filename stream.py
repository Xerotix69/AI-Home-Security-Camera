import cv2
import threading
from collections import deque
import time

frame = None
frameBuffer = deque(maxlen=300)
frameLock = threading.Lock()
buffer_ready = threading.Event()

def capture_frame():
    global frame
    global frameBuffer
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open video device")
        return
    else:
        print("Video device opened successfully")
    
    consecutive_failures = 0
    max_consecutive_failures = 5
    
    try:
        while True:
            success, captured_frame = camera.read()
            if not success:
                consecutive_failures += 1
                print(f"Failed to read frame. Consecutive failures: {consecutive_failures}")
                if consecutive_failures >= max_consecutive_failures:
                    print("Too many consecutive failures. Restarting camera.")
                    camera.release()
                    camera = cv2.VideoCapture(0)
                    if not camera.isOpened():
                        print("Error: Could not reopen video device")
                        return
                    consecutive_failures = 0
                continue
            
            consecutive_failures = 0
            
            with frameLock:
                print("ADDING FRAME")
                frame = captured_frame
                frameBuffer.append(frame)

    except Exception as e:
        print(f"An error occurred during frame capture: {str(e)}")
    finally:
        camera.release()
        print("Camera released")

def start_stream():
    capture_thread = threading.Thread(target=capture_frame)
    capture_thread.daemon = True
    capture_thread.start()
    print("Capture thread started")

def get_frames(n):
    global frameBuffer
    with frameLock:
        print(len(frameBuffer))
        if len(frameBuffer) >n:
            return frameBuffer[-n]
        else:
            print(f"Buffer not ready. Current size: {len(frameBuffer)}")
            return None
