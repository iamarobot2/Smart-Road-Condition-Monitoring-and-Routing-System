from ultralytics import YOLO

model = YOLO("yolo11m-seg.pt")
data = "../dataset/data.yaml"

if __name__ == "__main__":
    model.train(data=data, batch=0.80, imgsz=640, augment=True,
                device=0, epochs=100, patience=10, save=True, name="pothole_detector", plots=True, amp=False,
                cache=True, lr0 = 0.001)
