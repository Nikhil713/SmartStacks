import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
import datetime
import threading
import paho.mqtt.client as mqtt
import re
import json

# Constants
MAX_LENGTH = 50
MQTT_BROKER = "test.mosquitto.org"
TOPIC_SENSORS = "smartstacks/sensors"
TOPIC_ACTUATORS = "smartstacks/actuators"
TOPIC_PLAN = "smartstacks/plan"

timestamps = deque(maxlen=MAX_LENGTH)
temperature_data = deque(maxlen=MAX_LENGTH)
noise_data = deque(maxlen=MAX_LENGTH)

plan_instructions = [
    "Switch off light",
    "Open door"
]


def init_sensor_state():
    return {
        'temperature': 38.0,
        'sound': 70.0,
        'ultrasonic' :170,
        'humidity': 45.0,
        'fan_speed': 2,
        'raw_light': 3,
        'vacant_seats': 1,
        'noise_level': 'High',
        'outside_light': 86
    }

sensor_state = init_sensor_state()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code", rc)
    client.subscribe([(TOPIC_SENSORS, 0), (TOPIC_ACTUATORS, 0), (TOPIC_PLAN, 0)])

def on_message(client, userdata, msg):
    global plan_instructions

    try:
        topic = msg.topic
        payload = msg.payload.decode().strip()
        print(f"MQTT Payload from {topic}: {payload}")

        data = json.loads(payload)  # Parse JSON data

        # === SENSORS ===
        if topic == TOPIC_SENSORS:
            sensor_state['temperature'] = data.get("inside_temperature", sensor_state['temperature'])
            sensor_state['humidity'] = data.get("inside_humidity", sensor_state['humidity'])
            sensor_state['raw_light'] = data.get("raw_light", sensor_state['outside_light'])
            sensor_state['ultrasonic'] = data.get("ultrasonic", sensor_state['ultrasonic'])
            sensor_state['sound'] = data.get("sound", sensor_state['noise'])

            # Optional: compute vacant seats based on ultrasonic
            val = sensor_state['ultrasonic']
            sensor_state['vacant_seats'] = "1" if val > 200 else "0"

            # Optional: update mold risk if provided
            if "mold_risk_level" in data:
                sensor_state['mold_risk'] = data["mold_risk_level"]

        # # === ACTUATORS ===
        # if topic == TOPIC_ACTUATORS:
        #     sensor_state['fan_speed'] = data.get("fan_speed", sensor_state['fan_speed'])
        #     sensor_state['lighting_level'] = data.get("lighting_level", sensor_state['lighting_level'])
        #
        # # === PLAN ===
        # if topic == TOPIC_PLAN:
        #     # Expecting: {"plan": ["Switch off light", "Open door"]}
        #     if isinstance(data, dict) and "plan" in data:
        #         plan_instructions = data["plan"]

    except json.JSONDecodeError:
        print("Failed to decode JSON:", payload)
    except Exception as e:
        print("MQTT Error:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

app = dash.Dash(__name__)
app.title = "Smart Library Dashboard"

# ---------- Reusable UI Components ----------

def labeled_box(icon_url, content_id):
    return html.Div([
        html.Img(src=icon_url, style={'height': '50px', 'marginRight': '10px'}),
        html.Div(id=content_id, style={'fontSize': '35px', 'fontWeight': 'bold'})
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'border': '1px solid #ccc',
        'padding': '15px 20px',
        'margin': '10px',
        'width': '30%',
        'height': '100px',
        'borderRadius': '15px',
        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
        'backgroundColor': '#ffffff'
    })

def make_row(children):
    return html.Div(children, style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'flexWrap': 'wrap',
        'marginBottom': '20px'
    })

# ---------- Layout ----------
app.layout = html.Div([
    # html.H1("SMART LIBRARY", style={
    #     'textAlign': 'center',
    #     'fontSize': '60px',
    #     'margin': '20px 0',
    #     'color': '#00008B'
    # }),

    html.Div([
        html.Img(
            src="https://img.icons8.com/?size=100&id=FNHbyJNFRRf4&format=png&color=000000",  # Book icon URL
            style={'height': '60px', 'marginRight': '20px'}
        ),
        html.H1("SMART LIBRARY", style={
            'fontSize': '48px',
            'color': '#00008B',
            'margin': 0,
            'textAlign': 'center',
            'flex': 1
        }),
        html.Img(
            src="https://img.icons8.com/?size=100&id=FNHbyJNFRRf4&format=png&color=000000",  # Book icon URL
            style={'height': '60px', 'marginLeft': '20px'}
        ),
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',  # Center heading in the row
        'marginBottom': '30px'
    }),

    make_row([
        labeled_box("https://img.icons8.com/color/70/temperature--v1.png", 'temp-display'),
        labeled_box("https://img.icons8.com/color/70/fan.png", 'fan-status-display'),
        labeled_box("https://img.icons8.com/?size=100&id=A2IN67IJ01EN&format=png&color=000000", 'fan-speed-display')
    ]),

    make_row([
        labeled_box("https://img.icons8.com/?size=100&id=15352&format=png&color=000000", 'outside-light-display'),
        labeled_box("https://img.icons8.com/color/70/light-on.png", 'indoor-light-status-display'),
        labeled_box("https://img.icons8.com/color/70/desk-lamp.png", 'indoor-light-level-display')
    ]),

    make_row([
        labeled_box("https://img.icons8.com/color/70/hygrometer.png", 'humidity-display'),
        labeled_box("https://img.icons8.com/color/70/thermometer.png", 'mold-index-display'),
        labeled_box("https://img.icons8.com/color/70/warning-shield.png", 'mold-risk-display')
    ]),

    make_row([
        labeled_box("https://img.icons8.com/color/70/conference-call.png", 'seats-display'),
        labeled_box("https://img.icons8.com/color/70/speaker.png", 'noise-display')
    ]),

    html.Div([
        dcc.Graph(id='temp-graph', style={
            'width': '48%',
            'display': 'inline-block',
            'padding': '10px',
            'borderRadius': '10px',
            'backgroundColor': '#fff',
            'boxShadow': '0 4px 10px rgba(0,0,0,0.08)'
        }),
        # dcc.Graph(id='noise-graph', style={
        #     'width': '48%',
        #     'display': 'inline-block',
        #     'padding': '10px',
        #     'borderRadius': '10px',
        #     'backgroundColor': '#fff',
        #     'boxShadow': '0 4px 10px rgba(0,0,0,0.08)'
        # })
    html.Div(id='plan-display', style={
        'width': '48%',
        'padding': '20px',
        'fontSize': '20px',
        'backgroundColor': '#ffffff',
        'borderRadius': '10px',
        'boxShadow': '0 4px 10px rgba(0,0,0,0.08)'
    })
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    dcc.Interval(id='interval-update', interval=3000, n_intervals=0)
], style={
    'backgroundColor': '#e4f2f7',
        # '#fff5e6',  # 🍑 Peach background
    'minHeight': '100vh',
    'padding': '30px'
})

# ---------- Callback ----------
@app.callback(
    [Output('temp-display', 'children'),
     Output('fan-status-display', 'children'),
     Output('fan-speed-display', 'children'),
     Output('outside-light-display', 'children'),
     Output('indoor-light-status-display', 'children'),
     Output('indoor-light-level-display', 'children'),
     Output('humidity-display', 'children'),
     Output('mold-index-display', 'children'),
     Output('mold-risk-display', 'children'),
     Output('seats-display', 'children'),
     Output('noise-display', 'children'),
     Output('temp-graph', 'figure'),
     #Output('noise-graph', 'figure')],
     Output('plan-display', 'children')],
    [Input('interval-update', 'n_intervals')]
)
def update_dashboard(n):
    print(sensor_state)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    timestamps.append(now)
    temperature_data.append(sensor_state['temperature'])
    noise_data.append(sensor_state['sound'])

    mold_index = round(sensor_state['humidity'] / 10, 1)
    mold_risk = "High" if mold_index > 7 else "Low"
    fan_status = "ON" if sensor_state['fan_speed'] > 0 else "OFF"
    light_status = "ON" if sensor_state['raw_light'] > 0 else "OFF"
    noise_level = "High" if sensor_state['sound'] > 20 else "Low"

    # Color-coded HTML components
    fan_status_div = html.Div([
        html.Span("Fan Status: ", style={'color': 'black'}),
        html.Span("ON" if fan_status else "OFF", style={
            'color': '#009900' if fan_status else '#e74c3c'
        })
    ], style={'textAlign': 'center'})

    mold_risk_div = html.Div([
        html.Span("Risk of Mold: ", style={'color': 'black'}),
        html.Span(mold_risk, style={
            'color': '#009900' if mold_risk == 'Low' else '#e74c3c'
        })
    ], style={'textAlign': 'center'})

    light_status_div = html.Div([
        html.Span("Indoor Light: ", style={'color': 'black'}),
        html.Span("ON" if light_status else "OFF", style={
            'color': '#009900' if light_status else '#e74c3c'
        })
    ], style={'textAlign': 'center'})

    noise_level_div = html.Div([
        html.Span("Noise Level: ", style={'color': 'black'}),
        html.Span("High" if noise_level else "Low", style={
            'color': '#009900' if noise_level else '#e74c3c'
        })
    ], style={'textAlign': 'center'})

    temp_fig = go.Figure(go.Scatter(x=list(timestamps), y=list(temperature_data), mode='lines+markers'))
    temp_fig.update_layout(title='Temperature Over Time', xaxis_title='Time', yaxis_title='°C',
                           plot_bgcolor='#fefefe', paper_bgcolor='#ffffff')

    #noise_fig = go.Figure(go.Scatter(x=list(timestamps), y=list(noise_data), mode='lines+markers'))
    #noise_fig.update_layout(title='Noise Over Time', xaxis_title='Time', yaxis_title='dB',
    #                        plot_bgcolor='#fefefe', paper_bgcolor='#ffffff')
    plan_html = [html.H3("Current Plan Generated", style={'marginBottom': '10px'})]
    for i, instr in enumerate(plan_instructions, start=1):
        plan_html.append(html.Div(f"{i}. {instr}", style={'marginBottom': '5px'}))
    return (
        f"Temperature: {sensor_state['temperature']} °C",
        fan_status_div,
        f"Fan Speed: {sensor_state['fan_speed']}",
        f"Outside Light Intensity: {sensor_state['outside_light']}",
        light_status_div,
        f"Indoor Lighting Level: {sensor_state['raw_light']}",
        f"Humidity: {sensor_state['humidity']} %",
        f"Mold Index: {mold_index}",
        mold_risk_div,
        f"Vacant Seats: {sensor_state['vacant_seats']}",
        noise_level_div,
        temp_fig,
        plan_html
    )

if __name__ == '__main__':
    app.run(debug=True)