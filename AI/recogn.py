import torch
import cv2
import numpy as np
from PIL import Image
import insightface
from insightface.app.common import Face
import pickle
from insightface.model_zoo import model_zoo
from lines import *
from yolo import YOLOv8_face
import os
import time 
import json

def crop_images(image, bounding_boxes):
    """
    Crops the provided image based on the given bounding boxes.

    :param image: The source image to crop from.
    :param bounding_boxes: A list of bounding boxes, each defined as (x1, y1, x2, y2).
    :return: A list of cropped images.
    """
    cropped_images = []

    x1, y1, x2, y2 = bounding_boxes
    # Ensure coordinates are within image dimensions
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)

    # Crop and add to the list
    cropped = image[y1:y2, x1:x2]
    cropped_images.append(cropped)

    return cropped_images

class Recogniser:
    def __init__(self) -> None:
        self.detector = YOLOv8_face("./models/yolov8n-face.onnx")
        self.tracker = None
        self.rec_model = model_zoo.get_model(f'./models/webface_r50.onnx', providers=["CUDAExecutionProvider"])
        self.rec_model.prepare(ctx_id=0, input_size=(640, 640), det_thres=0.5)
        self.embeds = {}
        for i in os.listdir("./asset/"):
            self.save_embeds("./asset/"+i,i.split(".")[0])
        print("successfully loaded all the models")

    def save_embeds(self, path, name):
        img = cv2.imread(path)
        boxes, scores, classids, kpts = self.detect(img)
        n_kpts = []
        kp = kpts[0]
        for i in range(5):
            n_kpts.append([int(kp[i * 3]), int(kp[i * 3 + 1])])
        face = Face(bbox=boxes[0], kps=np.array(n_kpts), det_score=scores[0])
        self.embeds[name] = self.rec_model.get(img, face)
        with open('./embeds/embeds.pkl', 'wb') as file:
            pickle.dump(self.embeds, file)

    def search_flatten(self, emb, threshold=8.0):
        known_names = [k for k in self.embeds.keys()]
        k_embs = [i for i in self.embeds.values()]
        scr = []
        for k_emb in k_embs:
            score = np.dot(emb, k_emb.T)
            # score = np.clip(scores, 0., 1.)

            scr.append(score)
        name = known_names[np.argmax(np.array(scr))]
        if np.max(np.array(scr)) < threshold:
            return "Unknown",0.0
        return name, 1.00

    def detect(self,img):
        results = self.detector.detect(img)
        return results

    def draw(self, image, boxes, scores, kpts, name, scr):
        return self.detector.draw_detections(image, boxes, scores, kpts, name, scr)
    
    def get_embeds(self,img, boxes, scores, kpts):
        n_kpts = []
        kp = kpts
        for i in range(5):
            n_kpts.append([int(kp[i * 3]), int(kp[i * 3 + 1])])
        face = Face(bbox=boxes, kps=np.array(n_kpts), det_score=scores)
        self.rec_model.get(img, face)
        return face.normed_embedding

    def realtime_run(self):
        pass

if __name__ == "__main__":
    model = Recogniser()
    data = json.load(open('points.json', 'r'))
    border_line = np.array(data["points"])
    rtsp_addr = 0
    # rtsp_addr = "rtsp://admin:abcd1234@192.168.5.102:554/Streaming/Channels/101"

    cap = cv2.VideoCapture(rtsp_addr)
    prev_frame_time = time.time()
    if not cap.isOpened():
        print("Error: Unable to open camera")
        exit()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from camera")
            break

        # Perform object detection on the frame
        reslt = model.detect(frame)
        
        if reslt is not None:
            boxes, scores, classids, kpts = reslt
            names, recg_score = [],[]
            colliding = ""
            direc = ""
            for boxe, score, kpt in zip(boxes, scores, kpts):
                name,scor = model.search_flatten(model.get_embeds(frame, boxe, score, kpt ))#*[np.array(i,dtype=np.float64) for i in [boxe, score, kpt]]))
                names.append(name)
                recg_score.append(scor)
                # colliding = bounding_box_line_collision(boxe,border_line)
                # direc = point_position_relative_to_line(border_line,boxe)
                # Draw bounding boxes on the frame
            
            frame = model.draw(frame, boxes, scores, kpts, names, recg_score)
            
            # Display the resulting frame
            # Time when we finish processing for this frame
        new_frame_time = time.time()
        cv2.line(frame,border_line[0],border_line[1],(255, 0, 0),2)

        # Calculating the fps

        # Convert the time to seconds
        time_elapsed = new_frame_time - prev_frame_time
        fps = 1/time_elapsed if time_elapsed > 0 else 0

        # Updating the previous frame time to current time
        prev_frame_time = new_frame_time

        # Display the FPS on the frame
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3, cv2.LINE_AA)
        cv2.imshow('Real-time Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
