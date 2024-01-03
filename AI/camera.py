from recogn import *
import pickle as pkl
from datetime import datetime as dt
from constants import *

class Camera:
    def __init__(self, addr, server_addr, label,file=None) -> None:
        self.address = addr
        self.camera = cv2.VideoCapture(self.address)
        self.server_address = server_addr
        self.label = label
        self.model = Recogniser()
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
            
    def add_record(self, username,ddate, ttime):
        data = {
                "username":username,
                "datetime":str(ddate),
                "action":{
                    "type":self.label,
                    "time":str(ttime)
                    }
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
            colliding = ""
            direc = ""
            for boxe, score, kpt in zip(boxes, scores, kpts):
                name,scor = self.model.search_flatten(self.model.get_embeds(frame, boxe, score, kpt ))#*[np.array(i,dtype=np.float64) for i in [boxe, score, kpt]]))
                names.append(name)
                recg_score.append(scor)
                if name != "Unknown":
                    if len(self.data[name]) != 0:
                        last_seen = self.data[name][-1]
                        last_seen = dt.strptime(last_seen,"%H:%M:%S",)
                        current_time = dt.now()
                        current_time = dt.strptime(current_time.strftime('%H:%M:%S'),"%H:%M:%S")
                        dif = current_time - last_seen
                        if dif.seconds > 120:
                            self.update_record(name,dt.now())
                    else:
                        self.update_record(name,dt.now())
            frame = self.model.draw(frame, boxes, scores, kpts, names, recg_score)
            return boxes, names, frame
        
        else:
            return None, None, frame
    
    def update_record(self, username, ttime):
        date_string = ttime.strftime('%Y-%m-%d')
        time_string = ttime.strftime('%H:%M:%S')
        self.data[username].append(time_string)
        self.add_record(username,date_string,time_string)
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
