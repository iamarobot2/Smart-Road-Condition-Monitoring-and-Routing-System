import cv2
import os
from ultralytics import YOLO
import websocket
import json
import numpy as np
import threading
import math

model_path = "./model/bestseg.pt"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")
model = YOLO(model_path)

# Connect to the WebSocket server from the sensor server app for GPS data
gps_ws_url = "ws://192.168.20.11:8080/gps"
gps_ws = websocket.WebSocket()
gps_ws.connect(gps_ws_url)

gps_data = None
detected_potholes = []

def get_gps_location():
    """Read GPS data from the WebSocket server."""
    global gps_data
    while True:
        try:
            gps_data = gps_ws.recv()
            print(f"Received GPS data: {gps_data}")
        except Exception as e:
            print(f"Error reading GPS data: {e}")

gps_thread = threading.Thread(target=get_gps_location)
gps_thread.daemon = True
gps_thread.start()

def parse_gps_data(gps_data):
    """Parse GPS data from the WebSocket server."""
    if gps_data is None:
        return None, None
    try:
        gps_json = json.loads(gps_data)
        lat = gps_json.get("latitude")
        lon = gps_json.get("longitude")
        return lat, lon
    except Exception as e:
        print(f"Error parsing GPS data: {e}")
        return None, None

# Define a scale for severity based on segmented area (in cm^2)
def calculate_severity(area_cm2):
    if area_cm2 < 100:
        return "Low", (0, 255, 0)
    elif 100 <= area_cm2 < 400:
        return "Moderate", (0, 255, 255)
    else:
        return "High", (0, 0, 255)

# Focal length and reference distance (calibration parameters)
FOCAL_LENGTH = 800  # Example focal length in pixels
REFERENCE_DISTANCE = 10.0  # Standardized distance in meters

# Real-world area at reference distance for calibration
KNOWN_AREA = 2500.0  # Known pothole area in cm^2 at reference distance

def estimate_real_area(pixels_area, distance_m):
    """Convert pixel area to real-world area in cm^2."""
    return (pixels_area * KNOWN_AREA * REFERENCE_DISTANCE**2) / (FOCAL_LENGTH**2 * distance_m**2)

def is_pothole_detected(lat, lon):
    """Check if a pothole has already been detected at the given GPS coordinates."""
    for pothole in detected_potholes:
        if abs(pothole['lat'] - lat) < 0.0001 and abs(pothole['lon'] - lon) < 0.0001:
            return True
    return False

def adjust_gps_coordinates(lat, lon, distance, angle):
    """Adjust GPS coordinates based on distance and angle from the camera."""
    # Earth's radius in meters
    R = 6378137.0

    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Calculate new latitude and longitude
    new_lat_rad = lat_rad + (distance / R) * math.cos(angle)
    new_lon_rad = lon_rad + (distance / R) * math.sin(angle) / math.cos(lat_rad)

    # Convert new latitude and longitude from radians to degrees
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon

# Use the correct IP address from the IP Camera app for the video feed
mjpeg_url = 'http://192.168.20.2:8080/video'

cap = cv2.VideoCapture(mjpeg_url)

if not cap.isOpened():
    print("Error: Could not open video stream at", mjpeg_url)
    exit()

def process_frame():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break

        results = model.predict(frame, conf=0.6, iou=0.4)

        annotated_frame = frame.copy()
        lat, lon = parse_gps_data(gps_data)
        if lat and lon:
            cv2.putText(
                annotated_frame,
                f"GPS: ({lat:.6f}, {lon:.6f})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0, 
                (255, 255, 255),
                3,
            )
            # print(f"GPS coordinates: ({lat:.6f}, {lon:.6f})")

        if results[0].masks is not None and len(results[0].masks.data) > 0:
            for mask in results[0].masks.data:
                mask_np = mask.cpu().numpy().astype(np.uint8)
                if mask_np.size == 0:
                    continue
                mask_resized = cv2.resize(mask_np, (frame.shape[1], frame.shape[0]))
                pixels_area = cv2.countNonZero(mask_resized)

                # Approximate distance of the object (you might replace this with a depth sensor or stereo vision)
                distance_m = REFERENCE_DISTANCE  # Assuming constant distance; replace with actual distance estimation logic if available

                # Calculate real-world area of the pothole
                real_area_cm2 = estimate_real_area(pixels_area, distance_m)

                # Determine severity and color based on real-world area
                severity, color = calculate_severity(real_area_cm2)

                # Calculate the angle of the pothole in the frame
                x, y, w, h = cv2.boundingRect(mask_resized)
                angle = math.atan2(y + h / 2 - frame.shape[0] / 2, x + w / 2 - frame.shape[1] / 2)

                # Adjust GPS coordinates based on distance and angle
                pothole_lat, pothole_lon = adjust_gps_coordinates(lat, lon, distance_m, angle)

                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(
                    annotated_frame,
                    f"Severity: {severity} ({real_area_cm2:.1f} cm^2)",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, 
                    color,
                    3,
                )
                cv2.putText(
                    annotated_frame,
                    f"Location: ({pothole_lat:.6f}, {pothole_lon:.6f})",
                    (x, y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    color,
                    3,
                )
                print(f"Detected pothole at coordinates: ({pothole_lat:.6f}, {pothole_lon:.6f})")

                # Check if the pothole has already been detected
                if not is_pothole_detected(pothole_lat, pothole_lon):
                    detected_potholes.append({'lat': pothole_lat, 'lon': pothole_lon, 'severity': severity})
                    print(f"New pothole detected at coordinates: ({pothole_lat:.6f}, {pothole_lon:.6f}) with severity: {severity}")

                mask_colored = np.zeros_like(frame)
                mask_colored[mask_resized > 0] = color
                annotated_frame = cv2.addWeighted(annotated_frame, 1, mask_colored, 0.5, 0)

        cv2.imshow("Pothole Detection", cv2.resize(annotated_frame, (640, 480)))

        if lat and lon:
            print(f"GPS coordinates after frame: ({lat:.6f}, {lon:.6f})")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

frame_thread = threading.Thread(target=process_frame)
frame_thread.daemon = True
frame_thread.start()

while frame_thread.is_alive():
    frame_thread.join(1)

gps_ws.close()
cv2.destroyAllWindows()