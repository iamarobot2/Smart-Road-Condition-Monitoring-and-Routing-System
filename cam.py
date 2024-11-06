import cv2

# Use the correct IP address
mjpeg_url = 'http://192.168.20.3:8080/video'

# Attempt to open the video stream
cap = cv2.VideoCapture(mjpeg_url)

if not cap.isOpened():
    print("Error: Could not open video stream at", mjpeg_url)
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame")
        break

    cv2.imshow('Camera Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
