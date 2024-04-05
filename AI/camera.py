
from recogn import *
import pickle as pkl
from datetime import datetime as dt
from constants import *
import requests
import base64

AI_model = Recogniser()
class Camera:
    def __init__(self, addr, server_addr, label,file=None) -> None:
        self.address = addr
        self.camera = cv2.VideoCapture(self.address)
        self.server_address = server_addr
        self.label = label
        self.cam_index = 0
        # self.cam_addr = addres
        # resp = requests.get(self.server_address+f"add_camera/{self.label}?link={addres}")
        # print(resp.content)
        self.model = AI_model
        download_images(self.server_address,IMAGES_PATH)
        if file is None:
            self.data = {}
            for i in os.listdir(IMAGES_PATH):
                self.data[i.split(".")[0]] = []
        else:
            self.data = pkl.load(open(file,"rb"))
            for i in os.listdir(IMAGES_PATH):
                if not i.split(".")[0] in self.data.keys(): 
                    self.data[i.split(".")[0]] = []
            
    def add_record(self, username,ddate, ttime, bbox, image=False):
        data = {
                "username":username,
                "datetime":str(ddate),
                "action":{
                    "type":self.label,
                    "time":str(ttime)
                    },
                "link":self.address,
                "bbox":bbox,
                "image":image
                }
        response = requests.post(self.server_address+"add_record", json=data)
        print(response)
        return

    def update_frame(self):
        ret, frame = self.camera.read()
        
        if not ret:
            print("Error: Unable to read frame from camera")

        # Perform object detection on the frame
        reslt = self.model.detect(frame)
        
        if reslt is not None:
            boxes, scores, classids, kpts = reslt
            names, recg_score = [],[]
            for boxe, score, kpt in zip(boxes, scores, kpts):
                name,scor = self.model.search_flatten(self.model.get_embeds(frame, boxe, score, kpt ))#*[np.array(i,dtype=np.float64) for i in [boxe, score, kpt]]))
                names.append(name)
                recg_score.append(scor)
                if name != "Unknown":
                    framee = self.model.draw(frame, np.array([boxe]), np.array([scores]), np.array([kpts]), np.array([name]), np.array([recg_score]))
                    success, encoded_image = cv2.imencode('.jpg', framee)
                    image_base64 = base64.b64encode(encoded_image)
                    image_base64 = image_base64.decode('utf-8')
                    if len(self.data[name]) != 0:
                        last_seen = self.data[name][-1]
                        last_seen = dt.strptime(last_seen,"%H:%M:%S",)
                        current_time = dt.now()
                        current_time = dt.strptime(current_time.strftime('%H:%M:%S'),"%H:%M:%S")
                        dif = current_time - last_seen
                        if dif.seconds > 200:
                            self.update_record(name,dt.now(),boxe.tolist(),image_base64)
                    else:
                        self.update_record(name,dt.now(),boxe.tolist(),image_base64)
                    
            frame = self.model.draw(frame, boxes, scores, kpts, names, recg_score)
            return boxes, names, frame
        
        else:
            return None, None, frame
    
    def update_record(self, username, ttime, bbox, image=False):
        date_string = ttime.strftime('%Y-%m-%d')
        time_string = ttime.strftime('%H:%M:%S')
        self.data[username].append(time_string)
        self.add_record(username,date_string,time_string,bbox,image)
        self.save()

    def save(self):
        with open('data.pkl', 'wb') as file:
            pkl.dump(self.data, file)
    
    def release(self):
        self.camera.release()

    def refresh(self):
        self.data = {}
        for i in os.listdir(IMAGES_PATH):
            self.data[i.split(".")[0]] = []
