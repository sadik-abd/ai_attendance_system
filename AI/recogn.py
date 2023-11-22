import torch
import cv2
import numpy as np
from PIL import Image
import insightface
from insightface.app.common import Face
import pickle
from insightface.model_zoo import model_zoo
from yolo import YOLOv8_face
import os

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
    def __init__(self, size) -> None:
        self.detector = YOLOv8_face("./models/yolov8n-face.onnx")
        self.tracker = None
        self.rec_model = model_zoo.get_model(f'./models/w600k_mbf.onnx')
        self.rec_model.prepare(ctx_id=0, input_size=(640, 640), det_thres=0.5)
        self.embeds = {}
        for i in os.listdir("./asset/"):
            self.save_embeds("./asset/"+i,i.split(".")[0])
        # self.recogniser = InceptionResnetV1(pretrained="vggface2",device="cpu").eval()
        # weigths = torch.load("./models/face_net.pt")
        #self.recogniser.load_state_dict(weigths)
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

    def search_flatten(self, emb, threshold=0.5):
        pred_names = []
        known_names = [k for k in self.embeds.keys()]
        k_embs = [i for i in self.embeds.values()]
        scr = []
        for k_emb in k_embs:
            scores = np.dot(emb, k_emb.T)
            score = np.clip(scores, 0., 1.)

            idx = np.argmax(scores)
            scr.append(score)
        name = known_names[np.argmax(np.array(scr))]
        # if np.argmax(np.array(scr)) < 0.2:
        #     return "Unknown"
        return name

    def detect(self,img):
        results = self.detector.detect(img)
        return results

    def draw(self, image, boxes, scores, kpts, name):
        return self.detector.draw_detections(image, boxes, scores, kpts, name)
    
    def get_embeds(self,img, boxes, scores, kpts):
        n_kpts = []
        kp = kpts[0]
        for i in range(5):
            n_kpts.append([int(kp[i * 3]), int(kp[i * 3 + 1])])
        face = Face(bbox=boxes[0], kps=np.array(n_kpts), det_score=scores[0])
        return self.rec_model.get(img, face)


    def realtime_run(self):
        pass

if __name__ == "__main__":
    model = Recogniser("m")

    cap = cv2.VideoCapture(0)

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
            name = model.search_flatten(model.get_embeds(frame, boxes, scores, kpts))
            # Draw bounding boxes on the frame
            frame = model.draw(frame, boxes, scores, kpts, name)
            # Display the resulting frame
        cv2.imshow('Real-time Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
        