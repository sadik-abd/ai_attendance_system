from recogn import *
import pickle as pkl
from camera import Camera

cam = Camera(0,"http://127.0.0.1:5000/","entry")
prev_frame_time = time.time()
while True:
    boxes, names, frame = cam.update_frame()
    new_frame_time = time.time()

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