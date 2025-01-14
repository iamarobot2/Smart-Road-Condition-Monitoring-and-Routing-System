import websocket
import json
import threading
import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# Initialize global data structure to hold recent sensor values
sensor_data = {
    "android.sensor.accelerometer": {"x": [], "y": [], "z": []},
    "android.sensor.linear_acceleration": {"x": [], "y": [], "z": []},
    "android.sensor.gyroscope": {"x": [], "y": [], "z": []}
}

# Maximum number of points to display
max_data_points = 100


# WebSocket callback to handle incoming sensor data
def on_sensor_event(sensor_type, values, timestamp):
    if sensor_type in sensor_data:
        sensor_data[sensor_type]["x"].append(values[0])
        sensor_data[sensor_type]["y"].append(values[1])
        sensor_data[sensor_type]["z"].append(values[2])

        # Maintain buffer size
        if len(sensor_data[sensor_type]["x"]) > max_data_points:
            sensor_data[sensor_type]["x"].pop(0)
            sensor_data[sensor_type]["y"].pop(0)
            sensor_data[sensor_type]["z"].pop(0)


# Sensor WebSocket class
class Sensor:
    def __init__(self, address, sensor_type, on_sensor_event):
        self.address = address
        self.sensor_type = sensor_type
        self.on_sensor_event = on_sensor_event

    def on_message(self, ws, message):
        data = json.loads(message)
        values = data.get('values')
        timestamp = data.get('timestamp')
        self.on_sensor_event(sensor_type=self.sensor_type, values=values, timestamp=timestamp)

    def on_error(self, ws, error):
        print(f"Error occurred for {self.sensor_type}: {error}")

    def on_close(self, ws, close_code, reason):
        print(f"Connection closed for {self.sensor_type}. Reason: {reason}")

    def on_open(self, ws):
        print(f"Connected to {self.sensor_type} at {self.address}")

    def make_websocket_connection(self):
        ws = websocket.WebSocketApp(
            f"ws://{self.address}/sensor/connect?type={self.sensor_type}",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.run_forever()

    def connect(self):
        thread = threading.Thread(target=self.make_websocket_connection)
        thread.start()


# Connect to WebSocket for each sensor type
address = "192.168.5.155:8080"
Sensor(address=address, sensor_type="android.sensor.accelerometer", on_sensor_event=on_sensor_event).connect()
Sensor(address=address, sensor_type="android.sensor.linear_acceleration", on_sensor_event=on_sensor_event).connect()
Sensor(address=address, sensor_type="android.sensor.gyroscope", on_sensor_event=on_sensor_event).connect()

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Real-Time Sensor Data"),
    dcc.Interval(id='interval-component', interval=200, n_intervals=0),  # Update every second
    dcc.Graph(id="accelerometer-graph"),
    dcc.Graph(id="linear_acceleration-graph"),
    dcc.Graph(id="gyroscope-graph")
])


# Callback to update graphs every second
@app.callback(
    [Output('accelerometer-graph', 'figure'),
     Output('linear_acceleration-graph', 'figure'),
     Output('gyroscope-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Create plots for each sensor type
    figures = []
    for sensor_type in sensor_data:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=sensor_data[sensor_type]["x"], mode='lines', name='X-axis'))
        fig.add_trace(go.Scatter(y=sensor_data[sensor_type]["y"], mode='lines', name='Y-axis'))
        fig.add_trace(go.Scatter(y=sensor_data[sensor_type]["z"], mode='lines', name='Z-axis'))
        fig.update_layout(title=sensor_type, xaxis_title="Time", yaxis_title="Value",
                          yaxis=dict(range=[-20, 20]))  # Adjust range as needed
        figures.append(fig)

    return figures


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
