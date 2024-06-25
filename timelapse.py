import cv2
import os

def create_timelapse(imgs_folder, fps):
    output_video = "timelapse_video.mp4"

    images = [img for img in os.listdir(imgs_folder) if img.endswith(".jpg")]
    images.sort()

    if not images:
        print(f"No .jpg images found in {imgs_folder}")
        return

    frame = cv2.imread(os.path.join(imgs_folder, images[0]))
    if frame is None:
        print(f"Error: Unable to read image {images[0]}")
        return

    height, width, layers = frame.shape

    video = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for image in images:
        img_path = os.path.join(imgs_folder, image)
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Error: Unable to read image {image}. Skipping.")
            continue
        video.write(frame)

    video.release()
    cv2.destroyAllWindows()
    print(f"Timelapse video saved as {output_video}")

create_timelapse("timelapse_images", 30)
