

# Capture video
rtsp_addr = "rtsp://admin:abcd1234@192.168.5.102:554/Streaming/Channels/101"

import cv2
import numpy as np
import json

# Function to handle mouse clicks
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Save the coordinates on mouse click
        points.append((x, y))

        # Draw a circle at the clicked position
        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        # If two points are clicked, draw a line and save to JSON
        if len(points) == 2:
            cv2.line(frame, points[0], points[1], (255, 0, 0), 2)
            print(f"Points saved: {points}")
            save_points_to_json(points)
            points.clear()  # Clear the points list for new line

# Function to save points to a JSON file
def save_points_to_json(points):
    data = {'points': points}
    with open('points.json', 'w') as f:
        json.dump(data, f)

# Initialize a list to store points
points = []

# Capture video
cap = cv2.VideoCapture(rtsp_addr)

cv2.namedWindow("Video")
cv2.setMouseCallback("Video", click_event)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Video", frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
