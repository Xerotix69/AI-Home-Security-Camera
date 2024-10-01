import cv2
import os
import firebase_admin
from firebase_admin import credentials, storage, firestore, auth
import time
import json, jsonify
from datetime import datetime, timedelta
import requests


cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "jetson-security-camera.appspot.com",
    "databaseURL": "https://security-system-database-default-rtdb.europe-west1.firebasedatabase.app/"
})
bucket = storage.bucket()
db = firestore.client()

def login(email, password):
    try:
        api_key = "AIzaSyDXAIv0IlR1SjKLV6byrg5btfv3LAHzyXQ"
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        response = requests.post(url, json=payload)
        data = response.json()

        if 'idToken' in data:
            # Authentication successful
            id_token = data['idToken']
            return True, False
        else:
            return False, False

    except Exception as e:
        return False, e

def upload_source(encoded_file, targetPath):
    blob = bucket.blob(targetPath)
    blob.upload_from_string(encoded_file.tobytes(), content_type='image/jpeg')


    #blob.upload_from_filename(sourcePath)

    #os.remove(sourcePath)
    print(f"Uploaded {encoded_file} IMAGE to {targetPath}")

def screenshot(encoded_image, targetPath, targetPrefix, metadata):
    os.makedirs(targetPath, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    imageName = f"{targetPrefix}_{timestamp}.jpg"
    imagePath = os.path.join(targetPath, imageName)
    
    #cv2.imwrite(imagePath, frame)

    upload_source(encoded_image, f"{targetPath+"/images"}/{imageName}")

    if metadata:
        metadataName = f"{targetPrefix}_{timestamp}.json"
        metadataPath = os.path.join(targetPath, metadataName)

        with open(metadataPath, "w") as metadataFile:
            json.dump(metadata, metadataFile)

        upload_source(metadataPath, f"{targetPath+"/metadata"}/{metadataName}")

def create_timelapse(imgsFolder, fps, targetName, img_ext):
    images = [img for img in os.listdir(imgsFolder) if img.endswith(img_ext)]
    images.sort()

    if not images:
        print(f"No {img_ext} images found in {imgsFolder}")
        return

    frame = cv2.imread(os.path.join(imgsFolder, images[0]))
    if frame is None:
        print(f"Error: Unable to read image {images[0]}")
        return

    height, width, layers = frame.shape
    video = cv2.VideoWriter(targetName, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    for image in images:
        img_path = os.path.join(imgsFolder, image)
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Error: Unable to read image {image}. Skipping.")
            continue
        video.write(frame)

    video.release()
    cv2.destroyAllWindows()
    print(f"Timelapse video saved as {targetName}")

def clip_video(imgs, fps, seconds, targetPath, targetPrefix, metadata):
    os.makedirs(targetPath, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    videoName = f"{targetPrefix}_{timestamp}.mp4"
    
    videoPath = os.path.join(targetPath, videoName)

    target_imgs = fps * seconds

    if len(imgs) < target_imgs:
        print("Not enough images were recorded!")
        return

    clipped_frames = list(imgs)[-target_imgs:]
    height, width = clipped_frames[0].shape[:2]
    video = cv2.VideoWriter(videoPath, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    for frame in clipped_frames:
        video.write(frame)
    video.release()

    upload_source(videoPath, f"{targetPath+"/videos"}/{videoName}")

    if metadata:
        metadataName = f"{targetPrefix}_{timestamp}.json"
        metadataPath = os.path.join(targetPath, metadataName)

        with open(metadataPath, "w") as metadataFile:
            json.dump(metadata, metadataFile)

        upload_source(metadataPath, f"{targetPath+"/metadata"}/{metadataName}")

def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for error status codes

    return response.json()

def fetch_media(folderPath,type):
    blobs = bucket.list_blobs(prefix=folderPath+f"/{type}/")
    blobs2 = bucket.list_blobs(prefix=folderPath+f"/metadata/")
    expiration_time = datetime.now() + timedelta(hours=2)

    imageUrls = [blob.generate_signed_url(expiration=expiration_time) for blob in blobs if not blob.name.endswith("/")]
    metadata = [fetch_json(blob.generate_signed_url(expiration=expiration_time)) for blob in blobs2 if not blob.name.endswith("/")]
    return [imageUrls, metadata]

doc_ref = db.collection("logs").document()

def log(imgs, fps, seconds, location, img_ref, additional_data):
    data = {
        "Timestamp": time.strftime("%Y%m%d-%H%M%S"),
        "Location": location,
        "Extra": additional_data,
        "Reason": "test",
        "R"
        "Video": f"Test"
    }
    clip_video(imgs, fps, seconds, "logs", "clips", False)
    doc_ref = db.collection("logs").document()
    doc_ref.set(data)

def fetch_logs():
    docs = db.collection('logs').stream()

    log_data = []
    for doc in docs:
        data = doc.to_dict()
        log_data.append(data)

    return log_data

def zoom(zoomFactor,frame, frameWidth,frameHeight):

    frameWidth = frameWidth
    frameHeight = frameHeight

    zoomFactor = zoomFactor

    centerX, centerY = frameWidth // 2, frameHeight // 2
    newWidth, newHeight = int(frameWidth / zoomFactor), int(frameHeight / zoomFactor)
    
    topLeftX = int(max(centerX - newWidth // 2, 0))
    topLeftY = int(max(centerY - newHeight // 2, 0))

    croppedFrame = frame[topLeftY:topLeftY + newHeight, topLeftX:topLeftX  + newWidth]
    
    zoomedFrame = cv2.resize(croppedFrame, (int(frameWidth), int(frameHeight)))
    
    return zoomedFrame