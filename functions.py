import cv2
import os
import firebase_admin
from firebase_admin import credentials, storage
import time
import json
import jsonify

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "security-system-database.appspot.com",
    "databaseURL": "https://security-system-database-default-rtdb.europe-west1.firebasedatabase.app/"
})
bucket = storage.bucket()

def create_info(name, date,location, triggerReason, imgQuality):
    return {
        "name": name,
        "date": date,
        "location": location,
        "triggerReason": triggerReason,
        "imgQuality": imgQuality
    }

def upload_img(imgPath, targetPath):
    blob = bucket.blob(targetPath)
    blob.upload_from_filename(imgPath)

    os.remove(imgPath)
    print(f"Uploaded {imgPath} IMAGE to {targetPath}")

def upload_vid(vidPath, targetPath):
    blob = bucket.blob(targetPath)
    blob.upload_from_filename(vidPath)

    os.remove(vidPath)
    print(f"Uploaded {vidPath} VIDEO to {targetPath}")

def screenshot(frame, targetPath, targetPrefix, metadata):
    os.makedirs(targetPath, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    imageName = f"{targetPrefix}_{timestamp}.jpg"
    metadataName = f"{targetPrefix}_{timestamp}.json"

    imagePath = os.path.join(targetPath, imageName)
    metadataPath = os.path.join(targetPath, metadataName)

    cv2.imwrite(imagePath, frame)
    
    with open(metadataPath, 'w') as metadataFile:
        json.dump(metadata, metadataFile)

    upload_img(imagePath, f"{targetPath}/{imageName}")
    #upload_img(metadataPath, f"{targetPath}/{metadataName}")

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
    video = cv2.VideoWriter(targetName, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

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

def clip_video(imgs, fps, seconds, targetName, metaData):
    target_imgs = fps * seconds

    if len(imgs) < target_imgs:
        print("Not enough images were recorded!")
        return

    clipped_frames = list(imgs)[-target_imgs:]
    height, width = clipped_frames[0].shape[:2]
    video = cv2.VideoWriter(targetName, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for frame in clipped_frames:
        video.write(frame)
    video.release()
    upload_vid()

def get_images(folderPath):

    if not folderPath.endswith('/'):
        folderPath += '/'
    
    blobs = bucket.list_blobs(prefix=folderPath)
    
    imageUrls = [blob.generate_signed_url(expiration=3600) for blob in blobs]
    return jsonify(image_urls=imageUrls)