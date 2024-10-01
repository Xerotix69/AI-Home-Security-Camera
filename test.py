import cv2
import threading
from collections import deque

frame = None
frameBuffer = deque(maxlen=300)
frameLock = threading.Lock()

def capture_frame():
    global frame
    global frameBuffer

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open video device")
        return
    else:
        print("Video device opened successfully")
        
    try:
        while True:
            success, captured_frame = camera.read()
            if not success:
                break

            with frameLock:
                print("CAPTURED")
                frame = captured_frame
                frameBuffer.append(frame)
    finally:
        camera.release()

def start_stream():
    capture_thread = threading.Thread(target=capture_frame)
    capture_thread.daemon = True
    capture_thread.start()

def get_frames(n):
    with frameLock:
        if len(frameBuffer) > n:
            return frameBuffer[-n]
        else:
            #print("Buffer not ready. Current size:", len(frameBuffer))
            return None

def display_frames():
    """Continuously display the latest frame from the buffer."""
    while True:
        latest_frame = get_frames(1)
        if latest_frame is not None:
            cv2.imshow('Frame', latest_frame)  # Display the latest frame
        
        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()

# Start the stream in a separate thread
start_stream()

# Continuously display frames
display_frames()
