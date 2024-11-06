import cv2
from ultralytics import YOLO

model = YOLO("bestseg.pt")
video = "../assets/videos/mixkit-potholes-in-a-rural-road-25208-hd-ready.mp4"
cap = cv2.VideoCapture(video)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    results = model.predict(frame, conf=0.4,iou=0.3)
    annotated_frame = results[0].plot()
    cv2.imshow("Pothole detection", cv2.resize(annotated_frame, (640, 480)))
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()