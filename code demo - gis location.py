import cv2
from ultralytics import YOLO
import geopandas as gpd
from shapely.geometry import Point
import psycopg2

# Initialize YOLO model
model = YOLO("path_to_model/bestdect.pt")

# Video file
video = "path_to_video/video.mp4"
cap = cv2.VideoCapture(video)

# Function to calculate geographic coordinates (Example)
def calculate_geographic_coordinates(pixel_x, pixel_y, video_metadata):
    # Placeholder: Replace with logic to map pixel coordinates to geographic coordinates
    lat = video_metadata['latitude'] + (pixel_y * video_metadata['lat_scale'])
    lon = video_metadata['longitude'] + (pixel_x * video_metadata['lon_scale'])
    return lat, lon

# Initialize list to store pothole data
potholes_data = []

# Example video metadata (adjust for your use case)
video_metadata = {
    "latitude": 12.971598,  # Initial latitude
    "longitude": 77.594566,  # Initial longitude
    "lat_scale": 0.00001,  # Scale factor for latitude
    "lon_scale": 0.00001   # Scale factor for longitude
}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(frame, conf=0.6, iou=0.4)
    for detection in results[0].boxes:
        x1, y1, x2, y2 = map(int, detection.xyxy[0])  # Bounding box coordinates
        width = x2 - x1
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2  # Center of the bounding box
        
        # Calculate geographic coordinates of the pothole
        lat, lon = calculate_geographic_coordinates(center_x, center_y, video_metadata)
        
        # Append data
        potholes_data.append({"latitude": lat, "longitude": lon, "severity": width})

cap.release()

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    potholes_data,
    geometry=[Point(data["longitude"], data["latitude"]) for data in potholes_data],
    crs="EPSG:4326"  # WGS 84 coordinate system
)

# Save as GeoJSON
gdf.to_file("potholes.geojson", driver="GeoJSON")

# Alternatively, insert data into PostGIS
conn = psycopg2.connect("dbname=gis_db user=your_user password=your_password host=your_host port=5432")
cursor = conn.cursor()

for pothole in potholes_data:
    cursor.execute(
        """
        INSERT INTO potholes (latitude, longitude, severity, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """,
        (pothole["latitude"], pothole["longitude"], pothole["severity"], pothole["longitude"], pothole["latitude"])
    )

conn.commit()
cursor.close()
conn.close()
