import cv2
import os
from ultralytics import YOLO

# Load the YOLO model
model_path = r"C:/Users/Abishek/Downloaded/Documents/GitHub/Smart-Road-Condition-Monitoring-and-Routing-System/model/bestdect.pt"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")
model = YOLO(model_path)

# Path to the video
video = "./assets/videos/mixkit-potholes-in-a-rural-road-25208-hd-ready.mp4"
if not os.path.exists(video):
    raise FileNotFoundError(f"Video file not found: {video}")

cap = cv2.VideoCapture(video)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Define a scale for severity based on real-world width (in cm)
def calculate_severity(real_width_cm):
    if real_width_cm < 10:
        return "Low", (0, 255, 0)
    elif 10 <= real_width_cm < 20:
        return "Moderate", (0, 255, 255)
    else:
        return "High", (0, 0, 255)

# Focal length and reference distance (calibration parameters)
FOCAL_LENGTH = 800  # Example focal length in pixels
REFERENCE_DISTANCE = 10.0  # Standardized distance in meters

# Real-world width at reference distance for calibration
KNOWN_WIDTH = 50.0  # Known pothole width in cm at reference distance

def estimate_real_width(pixels_width, distance_m):
    """Convert pixel width to real-world width in cm."""
    return (pixels_width * KNOWN_WIDTH * REFERENCE_DISTANCE) / (FOCAL_LENGTH * distance_m)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Finished processing video.")
        break

    # Perform predictions on the frame
    results = model.predict(frame, conf=0.6, iou=0.4)

    # Annotate the frame and process detections
    annotated_frame = frame.copy()
    for detection in results[0].boxes:
        x1, y1, x2, y2 = map(int, detection.xyxy[0])
        width_pixels = x2 - x1

        # Approximate distance of the object (you might replace this with a depth sensor or stereo vision)
        distance_m = REFERENCE_DISTANCE  # Assuming constant distance; replace with actual distance estimation logic if available

        # Calculate real-world width of the pothole
        real_width_cm = estimate_real_width(width_pixels, distance_m)

        # Determine severity and color based on real-world width
        severity, color = calculate_severity(real_width_cm)

        # Overlay severity on the frame
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            annotated_frame,
            f"Severity: {severity} ({real_width_cm:.1f} cm)",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )

    # Display the frame with annotations
    cv2.imshow("Pothole Detection", cv2.resize(annotated_frame, (640, 480)))

    # Exit the loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
