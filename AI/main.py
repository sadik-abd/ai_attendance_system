from recogn import *
import pickle as pkl
from camera import Camera
from flask import Flask, Response
import threading
cam = Camera(0,"http://127.0.0.1:80/","entry")
prev_frame_time = time.time()
start_time = time.time()
app = Flask(__name__)
resp = None

def gen_frames():
    global start_time
    global prev_frame_time
    global resp
    while True:
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
        ret, buffer = cv2.imencode('.jpg', frame)
        
        resp = (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    def gen():
        global resp
        while True:
            yield resp
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    my_thread = threading.Thread(target=gen_frames)
    my_thread.start()
    app.run(port=3232)
    my_thread.join()
