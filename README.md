# 🚗 SMART ROAD CONDITION MONITORING AND OPTIMAL ROUTING SYSTEM USING YOLOv11

This project aims to enhance road safety by providing a navigation software that detects and maps road conditions, specifically potholes, in real-time using computer vision and deep learning. Leveraging the YOLOv11 model, the system accurately identifies potholes, assesses their severity, and determines their GPS-based location, updating the map continuously. The application includes an optimal routing feature, guiding drivers along the safest and most efficient routes by avoiding hazardous road segments. This comprehensive solution offers real-time alerts and intelligent routing, helping drivers avoid potential hazards and ensuring a smoother, safer driving experience.

## ✨ Key Features

- **Real-Time Detection**: YOLOv11’s speed and precision enable prompt identification of road anomalies.
- **Severity Assessment**: Each pothole’s severity is assessed to aid in decision-making.
- **Dynamic Mapping**: Road hazard data is continuously updated, creating a live map of current road conditions.
- **Optimal Routing**: An algorithm recommends the safest and most efficient routes by avoiding damaged road segments.

The system is adaptable across various vehicle platforms, making it suitable for diverse driving environments. Future enhancements will improve detection under challenging conditions, such as low light and adverse weather, further strengthening the system’s reliability and accuracy.

## 🗂️ Project Structure

- `SensordataPlot.py`: Handles the real-time plotting of sensor data.
- `sensordata.py`: Manages the websocket connection and data reception.
- `cam.py`: Captures video stream from a specified URL.
- `model/predict_seg.py`: Performs object segmentation using a YOLO model.
- `model/predict_dect.py`: Performs object detection using a YOLO model.
- `model/train.py`: Trains a YOLO model on the provided dataset.

## 📊 Data and Resources

- Videos and datasets are available [here](https://drive.google.com/drive/folders/1Ek4JjCteSU0B6NoKK0q62v8-HRmDATxX?usp=drive_link).
- Google Colab link for training: [Colab Notebook](https://colab.research.google.com/drive/1q68maJrnHwWhyiYtThARvkFmlDFnEh1c?usp=sharing).

## ⚙️ Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/iamarobot2/Smart-Road-Condition-Monitoring-and-Routing-System.git
    cd Final-Project
    ```

2. Create and activate the virtual environment:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## 🚀 Usage

### 📹 Video Stream

Run the `cam.py` script to capture and display the video stream:
```sh
python cam.py
```

### 🔍 Object Detection and Segmentation

Before running, ensure to download the video asset from the Google Drive and replace the path accordingly.

Run the `model/predict_seg.py` script for object segmentation:
```sh
python model/predict_seg.py
```

Run the `model/predict_dect.py` script for object detection:
```sh
python model/predict_dect.py
```

### 🏋️‍♂️ Training and Validation

Use the provided Google Colab notebook for training and validating the YOLO model:
[Colab Notebook](https://colab.research.google.com/drive/1q68maJrnHwWhyiYtThARvkFmlDFnEh1c?usp=sharing).

## 📜 License

This project is licensed under the MIT License.

## 👥 Authors

- Abishek R Paleri
- Ali Jasim
- Athul Mohan
- Avin Joshy