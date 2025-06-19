import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
import datetime
import threading
import paho.mqtt.client as mqtt
import json

# Constants
MAX_LENGTH = 50

timestamps = deque(maxlen=MAX_LENGTH)
temperature_data = deque(maxlen=MAX_LENGTH)
noise_data = deque(maxlen=MAX_LENGTH)

# Shared sensor state
def init_sensor_state():
    return {
        'temperature': 38.0,
        'noise': 70.0,
        'humidity': 45,
        'fan_speed': 2,
        'lighting_level': 3,
        'vacant_seats': 1,
        'noise_level': 'High'
    }

sensor_state = init_sensor_state()

# MQTT config
BROKER = "test.mosquitto.org"
PORT = 1883
CLIENT_ID = "raspberrypi_sensor_01"
TOPIC = "smartstacks/sensors"

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        for key in payload:
            if key in sensor_state:
                sensor_state[key] = payload[key]
        # Derive noise level
        sensor_state['noise_level'] = 'High' if sensor_state['noise'] > 75 else 'Low'
    except Exception as e:
        print("Error processing message:", e)

# Run MQTT in a separate thread
def start_mqtt():
    client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311, transport='tcp')
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("SMART LIBRARY", style={'textAlign': 'center', 'fontSize': '50px'}),

    html.Div([
        html.Div([
            html.Div("Temperature: 38°C", id='temp-display', style={'fontSize': '24px', 'border': '3px solid black', 'padding': '15px', 'margin': '15px'})
        ], style={'width': '45%', 'display': 'inline-block'}),

        html.Div([
            html.Div("Humidity: 45", id='humidity-display', style={'fontSize': '24px', 'border': '3px solid black', 'padding': '15px', 'margin': '15px'})
        ], style={'width': '45%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Div([
            html.Img(src='https://img.icons8.com/color/70/fan.png', style={'marginRight': '15px'}),
            html.Div("FAN SPEED: 2", id='fan-display', style={'fontSize': '22px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '15px'}),

        html.Div([
            html.Img(src='https://img.icons8.com/color/70/light-on.png', style={'marginRight': '15px'}),
            html.Div("LIGHTING LEVEL: 3", id='light-display', style={'fontSize': '22px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '15px'})
    ], style={'display': 'flex','justifyContent': 'space-around'}),

    html.Div([
        html.Div([
            html.Img(src='https://img.icons8.com/color/70/conference-call.png', style={'marginRight': '15px'}),
            html.Div("VACANT SEATS: 1", id='seats-display', style={'fontSize': '22px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '15px'}),

        html.Div([
            html.Img(src='https://img.icons8.com/color/70/speaker.png', style={'marginRight': '15px'}),
            html.Div("NOISE LEVEL: HIGH", id='noise-display', style={'fontSize': '22px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'margin': '15px'})
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    html.Div([
        dcc.Graph(id='temp-graph', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='noise-graph', style={'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div("RISK OF MOULD: HIGH!", style={'textAlign': 'center', 'color': 'red', 'fontSize': '36px', 'marginTop': '30px'}),

    dcc.Interval(id='interval-update', interval=3000, n_intervals=0)
])

@app.callback(
    [Output('temp-graph', 'figure'),
     Output('noise-graph', 'figure'),
     Output('temp-display', 'children'),
     Output('humidity-display', 'children'),
     Output('fan-display', 'children'),
     Output('light-display', 'children'),
     Output('seats-display', 'children'),
     Output('noise-display', 'children')],
    [Input('interval-update', 'n_intervals')]
)
def update_dashboard(n):
    now = datetime.datetime.now().strftime('%H:%M:%S')
    timestamps.append(now)
    temperature_data.append(sensor_state['temperature'])
    noise_data.append(sensor_state['noise'])

    temp_fig = go.Figure(go.Scatter(x=list(timestamps), y=list(temperature_data), mode='lines+markers'))
    temp_fig.update_layout(title='Temperature Over Time', xaxis_title='Time', yaxis_title='°C')

    noise_fig = go.Figure(go.Scatter(x=list(timestamps), y=list(noise_data), mode='lines+markers'))
    noise_fig.update_layout(title='Noise Over Time', xaxis_title='Time', yaxis_title='dB')

    return (
        temp_fig,
        noise_fig,
        f"Temperature: {sensor_state['temperature']} °C",
        f"Humidity: {sensor_state['humidity']} %",
        f"FAN SPEED: {sensor_state['fan_speed']}",
        f"LIGHTING LEVEL: {sensor_state['lighting_level']}",
        f"VACANT SEATS: {sensor_state['vacant_seats']}",
        f"NOISE LEVEL: {sensor_state['noise_level']}"
    )

if __name__ == '__main__':
    app.run(debug=True)