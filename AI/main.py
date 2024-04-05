
import cv2
import os
import signal
import time
from multiprocessing import Process, Queue, Event
from camera import Camera
import requests
def gen_frames(queue, stop_event, cctv_link, server_link, label):
    cam = Camera(cctv_link, server_link, label)
    response = requests.get(server_link+"/add_camera/"+label+"?link='"+cctv_link+"'")
    print(response.text)
    prev_frame_time = time.time()
    start_time = time.time()

    while not stop_event.is_set():
        boxes, names, frame = cam.update_frame()
        new_frame_time = time.time()
        time_elapsed = new_frame_time - prev_frame_time
        fps = 1 / time_elapsed if time_elapsed > 0 else 0
        prev_frame_time = new_frame_time

        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > 86400:  # Refresh every 24 hours
            cam.refresh()
            start_time = current_time

        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3, cv2.LINE_AA)
        queue.put(frame)
        time.sleep(0.01)  # Prevents overloading the queue with frames

def render_frames(queue, stop_event, cctv_link):
    cv2.namedWindow(cctv_link)
    while not stop_event.is_set():
        if not queue.empty():
            frame = queue.get()
            cv2.imshow(cctv_link, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    frame_queue = Queue(maxsize=10)
    stop_event = Event()

    # Set your parameters here
    cctv_link = input("Enter cctv link: ")
    label = input("Enter the label: ")
    server_link = input("Enter the server link: ")

    # Create and start the video capture process
    capture_process = Process(target=gen_frames, args=(frame_queue, stop_event, cctv_link, server_link, label))
    capture_process.start()

    try:
        # Main process handles video display
        render_frames(frame_queue, stop_event, cctv_link)
    finally:
        # Ensure the subprocess is stopped
        stop_event.set()
        capture_process.join()
