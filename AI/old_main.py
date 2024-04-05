from recogn import *
import pickle as pkl
from camera import Camera
from flask import Flask, Response, stream_with_context
import threading
import sys
import signal
import argparse

# Create the parser
# Prompt the user to enter the values for each variable
cctv_link = input("Enter CCTV Link: ")
video_port = int(os.getenv('3333', 5000))
label = input("Enter Label: ")
server_link = input("Enter Server Link: ")

# Convert video_port to an integer, since input() returns a string
video_port = int(video_port)

# Example usage of the variables
print("CCTV Link:", cctv_link)
print("Video Port:", video_port)
print("Label:", label)
print("Server Link:", server_link)



cam = Camera(cctv_link,server_link,label,addres=f"'http://127.0.0.1:{video_port}/video_feed'")
prev_frame_time = time.time()
start_time = time.time()
app = Flask(__name__)
resp = None
stopp = False

def gen_frames():
    global start_time
    global prev_frame_time
    global resp
    global stopp
    while not stopp:
        boxes, names, frame = cam.update_frame()
        new_frame_time = time.time()

        # Calculating the fps

        # Convert the time to seconds
        time_elapsed = new_frame_time - prev_frame_time
        fps = 1/time_elapsed if time_elapsed > 0 else 0

        # Updating the previous frame time to current time
        prev_frame_time = new_frame_time

        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > 86400:  # 86400 seconds in a day
            cam.refresh()
            start_time = current_time  
        # Display the FPS on the frame
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3, cv2.LINE_AA)
        cv2.imshow("AI Feed",frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        
        resp = (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def stop_running_bitch():
    time.sleep(3)
    os.kill(os.getpid(), signal.SIGINT)
@app.route('/video_feed')
def video_feed():
    def gen():
        global resp
        while True:
            yield resp
    return Response(stream_with_context(gen()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stop")
def stop():
    global stopp
    stopp = True
    my_thread.join()
    mth = threading.Thread(target=stop_running_bitch)
    mth.start()
    return {
        "message" : "Stopping in 5 seconds"
    }
    

    

my_thread = threading.Thread(target=gen_frames)
my_thread.start()
print("Starting in 4 seconds")
time.sleep(4)
app.run(port=video_port)