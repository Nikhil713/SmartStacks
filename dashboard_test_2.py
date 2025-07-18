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
    "Instruction 1",
    "Instruction 2"
]


def init_sensor_state():
    return {
        'inside_temperature': 38.0,
        'inside_humidity': 45.0,
        'raw_light': 3,
        'ultrasonic' :170,
        'sound': 70.0,
        'outside_temperature' : 30.0,
        'outside_humidity' : 55.0,
        'mold_risk_level': 'LOW'
        # 'mold_index' : 8
        # 'vacant_seats': 1,
        # 'noise_level': 'High',
        #'mold_risk_level' : 0
    }
def init_actuator_state():
    return {
        'vacant_seats': 1,
        'noise_level': 'High',
        'fan_speed': 2,
        'led_level' : 3
    }


sensor_state = init_sensor_state()
actuator_state = init_actuator_state()

bg_colour_mold = '#ffffff'
#define bg colour
if sensor_state['mold_risk_level'] == 'HIGH':
    bg_colour_mold = '#FF9793'
elif sensor_state['mold_risk_level'] == 'MEDIUM':
    bg_colour_mold = '#FFFFC5'
elif sensor_state['mold_risk_level'] == 'LOW':
    bg_colour_mold = '#e6ffe6'


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
            sensor_state['inside_temperature'] = data.get("inside_temperature", sensor_state['inside_temperature'])
            sensor_state['inside_humidity'] = data.get("inside_humidity", sensor_state['inside_humidity'])
            sensor_state['raw_light'] = data.get("raw_light", sensor_state['raw_light'])
            sensor_state['ultrasonic'] = data.get("ultrasonic", sensor_state['ultrasonic'])
            sensor_state['sound'] = data.get("sound", sensor_state['sound'])
            sensor_state['outside_temperature'] = round(data.get("outside_temperature", sensor_state['outside_temperature']),2)
            sensor_state['outside_humidity'] = data.get("outside_humidity", sensor_state['outside_humidity'])
            sensor_state['mold_risk_level'] = data.get("mold_risk_level", sensor_state['mold_risk_level'])

        # === ACTUATORS ===
        if topic == TOPIC_ACTUATORS:
            actuator_state['fan_speed'] = data.get("fan_speed", actuator_state['fan_speed'])
            actuator_state['lighting_level'] = data.get("lighting_level", actuator_state['lighting_level'])
            actuator_state['vacant_seats'] = data.get("vacant_seats", actuator_state['vacant_seats'])
            # actuator_state['mold_risk_level'] = data.get("mold_risk_level", actuator_state['mold_risk_level'])

        # # === PLAN ===
        # if topic == TOPIC_PLAN:
        #     # Expecting: {"plan": ["Switch off light", "Open door"]}
        #     if isinstance(data, dict) and "plan" in data:
        #         plan_instructions = data["plan"]
        # === PLAN ===
        if topic == TOPIC_PLAN:
            # Expecting a simple list: ["Switch off light", "Open door"]
            if isinstance(data, list):
                plan_instructions = data


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
        html.Img(src=icon_url, style={'height': '30px', 'marginRight': '10px'}),
        html.Div(id=content_id, style={'fontSize': '25px', 'fontWeight': 'bold'})
    ], style={
        'display': 'flex',
        'width' : '100%',
        'alignItems': 'center',
        'justifyContent': 'center',
        # 'border': '1px solid #ccc',
        # 'padding': '15px 20px',
        # 'margin': '10px',
        # 'width': '30%',
        'height': '100px',
        # 'borderRadius': '15px',
        # 'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
        # 'backgroundColor': '#ffffff'
    })

# def make_row(children):
#     return html.Div(children, style={
#         'display': 'flex',
#         'justifyContent': 'space-around',
#         'flexWrap': 'wrap',
#         'marginBottom': '20px'
#     })

def battery_indicator(label, level, max_level=3, color="#4CAF50"):
    filled_percent = (level / max_level) * 100

    return html.Div([
        html.Div(label, style={
            'fontSize': '25px',
            'marginRight': '15px',
            'whiteSpace': 'nowrap'
        }),

        html.Div([
            html.Div(style={
                'width': f'{filled_percent}%',
                'height': '100%',
                'backgroundColor': color,
                'borderRadius': '7px 0 0 7px' if filled_percent < 100 else '7px',
                'transition': 'width 0.5s ease'
            })
        ], style={
            'width': '120px',
            'height': '20px',
            'border': '2px solid #999',
            'borderRadius': '7px',
            'backgroundColor': '#e0e0e0',
            'overflow': 'hidden',
            'position': 'relative',
            'boxShadow': 'inset 0 1px 3px rgba(0,0,0,0.2)'
        }),

        html.Div(f"{level}/{max_level}", style={
            'marginLeft': '10px',
            'fontSize': '14px',
            'color': '#444'
        })
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'marginBottom': '15px'
    })


app.layout = html.Div([
    # Header
    html.Div([
        html.Img(
            src="https://img.icons8.com/?size=100&id=FNHbyJNFRRf4&format=png&color=000000",
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
            src="https://img.icons8.com/?size=100&id=FNHbyJNFRRf4&format=png&color=000000",
            style={'height': '60px', 'marginLeft': '20px'}
        ),
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'marginBottom': '30px'
    }),

    # --- Three Main Cards ---
    html.Div([
        # Card 1 - Inside Weather
        html.Div([
            html.H3("Inside Weather", style={'textAlign': 'center', 'fontSize': '32px'}),
            labeled_box("https://img.icons8.com/color/70/temperature--v1.png", 'temp-display'),
            labeled_box("https://img.icons8.com/color/70/hygrometer.png", 'humidity-display'),
            labeled_box("https://img.icons8.com/color/70/light-on.png", 'indoor-light-level-display')
        ], style={
            'width': '30%',
            'padding': '15px',
            'backgroundColor': '#ffffff',
            'borderRadius': '15px',
            'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
            'margin': '10px'
        }),

        # Card 2 - Outside Weather
        html.Div([
            html.H3("Outside Weather", style={'textAlign': 'center', 'fontSize': '32px'}),
            labeled_box("https://img.icons8.com/color/70/thermometer.png", 'outside-temp-display'),
            labeled_box("https://img.icons8.com/color/70/hygrometer.png", 'outside-humidity-display'),
            labeled_box("https://img.icons8.com/color/70/speaker.png", 'noise-display')
        ], style={
            'width': '30%',
            'padding': '15px',
            'backgroundColor': '#ffffff',
            'borderRadius': '15px',
            'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
            'margin': '10px'
        }),

        # Card 3 - Actuator Status
        html.Div([
            html.H3("Actuator Status", style={'textAlign': 'center', 'fontSize': '32px'}),
            labeled_box("https://img.icons8.com/color/70/fan.png", 'fan-speed-display'),
            labeled_box("https://img.icons8.com/color/70/desk-lamp.png", 'indoor-light-status-display'),
            labeled_box("https://img.icons8.com/color/70/conference-call.png", 'seats-display')
        ], style={
            'width': '30%',
            'padding': '15px',
            'backgroundColor': '#ffffff',
            'borderRadius': '15px',
            'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
            'margin': '10px'
        })
    ], style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'flexWrap': 'wrap',
        'marginBottom': '20px',
    }),

    # Mold Risk Message
    html.Div([
        labeled_box("https://img.icons8.com/color/70/warning-shield.png", 'mold-risk-display')
    ], style={
        'textAlign': 'center',
        'fontSize': '25px',
        'marginBottom': '30px',
        'fontWeight': 'bold',
        # 'width': '30%',
        'padding': '15px',
        'backgroundColor': bg_colour_mold,
        'borderRadius': '15px',
    }),

    # Graph and Plan Section
    html.Div([
        dcc.Graph(id='temp-graph', style={
            'width': '48%',
            'display': 'inline-block',
            'padding': '10px',
            'borderRadius': '10px',
            'backgroundColor': '#fff',
            'boxShadow': '0 4px 10px rgba(0,0,0,0.08)'
        }),
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
    'backgroundImage': 'url("/assets/lib_bg2.jpg")',
    'backgroundSize': 'cover',
    'backgroundRepeat': 'no-repeat',
    'backgroundPosition': 'center',
    # 'backgroundColor': '#e4f2f7',
    'minHeight': '100vh',
    'padding': '30px'
})

# ---------- Callback ----------
@app.callback(
    [Output('temp-display', 'children'),
     Output('humidity-display', 'children'),
     Output('indoor-light-level-display', 'children'),
     Output('outside-temp-display', 'children'),
     Output('outside-humidity-display', 'children'),
     Output('noise-display', 'children'),
     Output('fan-speed-display', 'children'),
     Output('indoor-light-status-display', 'children'),
     Output('seats-display', 'children'),
     # Output('mold-index-display', 'children'),
     Output('mold-risk-display', 'children'),
     Output('temp-graph', 'figure'),
     Output('plan-display', 'children')],
    [Input('interval-update', 'n_intervals')]
)

def update_dashboard(n):
    print(sensor_state)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    timestamps.append(now)
    temperature_data.append(sensor_state['inside_temperature'])
    noise_data.append(sensor_state['sound'])

    # mold_risk_level = "High" if actuator_state['mold_risk_level'] > 7 else "Low"
    # fan_status = "ON" if actuator_state['fan_speed'] > 0 else "OFF"
    # light_status = "ON" if sensor_state['raw_light'] > 0 else "OFF"
    # noise_level = "High" if sensor_state['sound'] > 20 else "Low"

    fan_speed_div = battery_indicator("Fan Speed", actuator_state['fan_speed'], max_level=3, color="#4caf50")

    indoor_light_div = battery_indicator("Indoor Light", actuator_state['led_level'], max_level=3,
                                         color="#ffc107")

    # Color-coded HTML components
    # fan_status_div = html.Div([
    #     html.Span("Fan Status: ", style={'color': 'black'}),
    #     html.Span("ON" if fan_status else "OFF", style={
    #         'color': '#009900' if fan_status else '#e74c3c'
    #     })
    # ], style={'textAlign': 'center'})

    # mold_risk_div = html.Div([
    #     html.Span("Risk of Mold: ", style={'color': 'black'}),
    #     html.Span(mold_risk, style={
    #         'color': '#e74c3c' if mold_risk == 'High' else '#009900'
    #     })
    # ], style={'textAlign': 'center'})

    # light_status_div = html.Div([
    #     html.Span("Indoor Light: ", style={'color': 'black'}),
    #     html.Span("ON" if light_status else "OFF", style={
    #         'color': '#009900' if light_status else '#e74c3c'
    #     })
    # ], style={'textAlign': 'center'})
    #
    # noise_level_div = html.Div([
    #     html.Span("Noise Level: ", style={'color': 'black'}),
    #     html.Span("High" if noise_level else "Low", style={
    #         'color': '#009900' if noise_level else '#e74c3c'
    #     })
    # ], style={'textAlign': 'center'})

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
        f"Temperature: {sensor_state['inside_temperature']} °C",
        f"Humidity: {sensor_state['inside_humidity']} %",
        f"Lighting Intensity: {sensor_state['raw_light']}",
        f"Temperature: {sensor_state['outside_temperature']} °C",
        f"Humidity: {sensor_state['outside_humidity']} %",
        #f"Fan Speed: {actuator_state['fan_speed']}",
        f"Noise Level: {actuator_state['noise_level']}",
        fan_speed_div,
        indoor_light_div,
        f"Vacant Seats: {actuator_state['vacant_seats']}",
        # f"Mold Index: {sensor_state['mold_index']}",
        f"Mold Risk: {sensor_state['mold_risk_level']}",
        # f"Mold Risk: {mold_risk_level}",
        #noise_level_div,
        temp_fig,
        plan_html
    )


if __name__ == '__main__':
    app.run(debug=True)