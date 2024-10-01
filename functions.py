import cv2
import os
import firebase_admin
from firebase_admin import credentials, storage, firestore
import time
import json
import tempfile
import google.cloud.firestore

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "jetson-security-camera.appspot.com",
    "databaseURL": "https://security-system-database-default-rtdb.europe-west1.firebasedatabase.app/"
})
bucket = storage.bucket()
db = firestore.client()

def upload_source(source, savePath, sourceType):
    blob = bucket.blob(savePath)
    if sourceType == "image":
        blob.upload_from_string(source.tobytes(), content_type='image/jpeg')
    elif sourceType == "video":
        blob.upload_from_filename(source.name)

    print(f"Uploaded to {savePath}")

def upload_metadata_to_firestore(document_id, metadata):
    doc_ref = db.collection('images_metadata').document(document_id)
    doc_ref.set(metadata)
    print(f"Metadata uploaded to Firestore with ID: {document_id}")

def create_metadata(cameraID = None, utcTime = None, time_stamp: str = time.strftime("%Y%m%d-%H%M%S"), reason: str = "N/A", source: str = "N/A", resolution: str = "N/A", cameraLocation: str = "Unknown") -> dict:
    metadata = {
        "camera_id": cameraID,
        "time_stamp": time_stamp,
        "utc_time": utcTime,
        "location": cameraLocation,
        "trigger_reason": reason,
        "source_type": source,
        "image_resolution": resolution
    }
    #CAMERA ID (FRONT GATE CAMERA)
    return metadata

def take_snapshot(frame, savePath, sourceType) -> None:
    ret, encoded_image = cv2.imencode('.jpg', frame)

    cTime = time.strftime("%Y%m%d-%H%M%S")
    metadata = create_metadata(cTime=cTime, source = sourceType)
    
    imageName = f"{sourceType}_{cTime}"
    ext = "jpg"
    
    finalPath = f"{savePath+"/images"}/{imageName}.{ext}"

    upload_source(encoded_image, finalPath, sourceType)
    upload_metadata_to_firestore(imageName, metadata)

def record_clip(frames, fps, seconds, savePath, sourceType):
    targetImgs = fps * seconds
    if len(frames) < targetImgs:
        print("Not enough images were recorded!")
        return

    cTime = time.strftime("%Y%m%d-%H%M%S")

    videoName = f"{sourceType}_{cTime}"
    ext = "mp4v"
    finalPath = f"{savePath+"/videos"}/{videoName}.{ext}"
   
    clippedFrames = list(frames)[-targetImgs:]
    height, width = clippedFrames[0].shape[:2]

    path = os.path.join("temp")
    with tempfile.NamedTemporaryFile(suffix=".mp4", dir=path) as temp:
        videoWriter = cv2.VideoWriter(temp.name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        for frame in clippedFrames:
            videoWriter.write(frame)
        videoWriter.release()

        upload_source(temp, finalPath, sourceType)

def filter_events(collectionName, cameraID=None, sourceType=None, location=None, startDate=None, endDate=None) -> list:
    ref = db.collection(collectionName)
    """
    # Apply filters using keyword arguments
    filters = []
    
    if cameraID:
        filters.append(('camera_id', '==', cameraID))
    
    if sourceType:
        filters.append(('type', '==', sourceType))
    
    if location:
        filters.append(('location', '==', location))
    
    if startDate and endDate:
        filters.append(('timestamp', '>=', startDate))
        filters.append(('timestamp', '<=', endDate))
    
    # Apply all filters in a single call using 'filter' method
    for f in filters:
        query = query.where(*f)
    
    # Always order by timestamp
    query = query.order_by('timestamp')

    # Execute the query and collect results
    results = []
    print("event")
    for event in query.stream():
        print(event)
        results.append(event.to_dict())
    """
    query = ref.where('camera_id', '==', cameraID)
        
    results = query.stream()
    users = []
    for doc in results:
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        users.append(user_data)
    print("RETRUNGIN!!!")
    return users
"""
cities_ref = db.collection("cities")

denver_query = cities_ref.where(filter=FieldFilter("state", "==", "CO")).where(
    filter= ("name", "==", "Denver")
)
large_us_cities_query = cities_ref.where(
    filter=FieldFilter("state", "==", "CA")
).where(filter=FieldFilter("population", ">", 1000000))

"""