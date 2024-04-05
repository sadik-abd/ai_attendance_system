from flask import Flask, Response, stream_with_context, request
import cv2
from multiprocessing import Process, Queue, Event

app = Flask(__name__)

def capture_frames(rtsp_url, queue, stop_event):
    cap = cv2.VideoCapture(rtsp_url)
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        queue.put(buffer.tobytes())
    cap.release()

def gen_frames(camera_url):
    q = Queue()
    stop_event = Event()
    p = Process(target=capture_frames, args=(camera_url, q, stop_event))
    p.start()
    try:
        while True:
            if q.empty():
                # Wait a bit for the queue to get filled
                continue
            frame = q.get()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # Stop the streaming process once the client disconnects
        stop_event.set()
        p.join()

@app.route('/video/')
def video():
    cam_addr = request.args.get("link")
    return Response(gen_frames(cam_addr),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6677, debug=True, threaded=True)
