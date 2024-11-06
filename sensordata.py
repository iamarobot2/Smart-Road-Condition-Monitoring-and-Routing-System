import websocket
import json


def on_message(ws, message):
    values = json.loads(message)['values']
    type = json.loads(message)['type']
    print("type = ", type)
    print("values = ", values)


def on_error(ws, error):
    print("error occurred")
    print(error)


def on_close(ws, close_code, reason):
    print("connection close")
    print("close code : ", close_code)
    print("reason : ", reason)


def on_open(ws):
    print("connected")


def connect(url):
    ws = websocket.WebSocketApp(url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()

connect(
    'ws://192.168.150.76:8080/sensors/connect?types=["android.sensor.accelerometer","android.sensor.linear_acceleration","android.sensor.gyroscope","android.sensor.magnetic_field","android.sensor.gravity"]')