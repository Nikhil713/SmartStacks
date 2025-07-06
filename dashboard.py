import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
import datetime
import threading
import paho.mqtt.client as mqtt
import re

# Constants
MAX_LENGTH = 50
MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "smartstacks/sensors"

timestamps = deque(maxlen=MAX_LENGTH)
temperature_data = deque(maxlen=MAX_LENGTH)
noise_data = deque(maxlen=MAX_LENGTH)

def init_sensor_state():
    return {
        'temperature': 38.0,
        'noise': 70.0,
        'ultrasonic' :170,
        'humidity': 45.0,
        'fan_speed': 2,
        'lighting_level': 3,
        'vacant_seats': 1,
        'noise_level': 'High',
        'outside_light': 86
    }

sensor_state = init_sensor_state()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode().strip()
        print("MQTT Payload:", payload)

        if "temp=" in payload:
            match = re.search(r"temp=([\d.]+),\s*humidity=([\d.]+)", payload)
            if match:
                sensor_state['temperature'] = float(match.group(1))
                sensor_state['humidity'] = float(match.group(2))

        elif "LDR raw=" in payload:
            match = re.search(r"LDR raw=(\d+),\s*intensity=(\d+)", payload)
            if match:
                sensor_state['outside_light'] = int(match.group(1))
                sensor_state['lighting_level'] = int(match.group(2))

        elif payload.isdigit():
            sensor_state['ultrasonic'] = int(payload)
            val = sensor_state['ultrasonic']
            sensor_state['vacant_seats'] = ( "1" if val > 200 else "0")

        # elif payload.isdigit():
        #     sensor_state['noise'] = int(payload)
        #     val = sensor_state['noise']
        #     sensor_state['noise_level'] = (
        #         "High" if val > 70 else "Moderate" if val > 50 else "Low"
        #     )
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
        dcc.Graph(id='noise-graph', style={
            'width': '48%',
            'display': 'inline-block',
            'padding': '10px',
            'borderRadius': '10px',
            'backgroundColor': '#fff',
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
     Output('noise-graph', 'figure')],
    [Input('interval-update', 'n_intervals')]
)
def update_dashboard(n):
    print(sensor_state)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    timestamps.append(now)
    temperature_data.append(sensor_state['temperature'])
    noise_data.append(sensor_state['noise'])

    mold_index = round(sensor_state['humidity'] / 10, 1)
    mold_risk = "High" if mold_index > 7 else "Low"
    fan_status = "ON" if sensor_state['fan_speed'] > 0 else "OFF"
    light_status = "ON" if sensor_state['lighting_level'] > 0 else "OFF"
    noise_level = "High" if sensor_state['noise'] > 20 else "Low"

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

    noise_fig = go.Figure(go.Scatter(x=list(timestamps), y=list(noise_data), mode='lines+markers'))
    noise_fig.update_layout(title='Noise Over Time', xaxis_title='Time', yaxis_title='dB',
                            plot_bgcolor='#fefefe', paper_bgcolor='#ffffff')

    return (
        f"Temperature: {sensor_state['temperature']} °C",
        fan_status_div,
        f"Fan Speed: {sensor_state['fan_speed']}",
        f"Outside Light Intensity: {sensor_state['outside_light']}",
        light_status_div,
        f"Indoor Lighting Level: {sensor_state['lighting_level']}",
        f"Humidity: {sensor_state['humidity']} %",
        f"Mold Index: {mold_index}",
        mold_risk_div,
        f"Vacant Seats: {sensor_state['vacant_seats']}",
        noise_level_div,
        temp_fig,
        noise_fig
    )

if __name__ == '__main__':
    app.run(debug=True)
