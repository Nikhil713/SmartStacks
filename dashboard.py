import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from collections import deque
import datetime
import threading
import paho.mqtt.client as mqtt
import re
import json
import pandas as pd
import io
import base64
from dash import ctx


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
        'mold_risk_level': 'HIGH'
        # 'mold_index' : 8
        # 'vacant_seats': 1,
        # 'noise_level': 'High',
        #'mold_risk_level' : 0
    }
def init_actuator_state():
    return {
        'occupied': True,
        'fan_speed': 2,
        'light_level' : 3,
        "sound_level": "Off"
    }


sensor_state = init_sensor_state()
actuator_state = init_actuator_state()

# def bgcolour():
#     if sensor_state['mold_risk_level'] == 'HIGH':
#         return '#FF9793'
#     elif sensor_state['mold_risk_level'] == 'MEDIUM':
#         return '#FFFFC5'
#     elif sensor_state['mold_risk_level'] == 'LOW':
#         return '#e6ffe6'

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
            actuator_state['light_level'] = data.get("light_level", actuator_state['light_level'])
            actuator_state['occupied'] = data.get("occupied", actuator_state['occupied'])
            actuator_state['sound_level'] = data.get("sound_level", actuator_state['sound_level'])
            # actuator_state['vacant_seats'] = 1 if sensor_state['ultrasonic']> 50 else 0
            # actuator_state['mold_risk_level'] = data.get("mold_risk_level", actuator_state['mold_risk_level'])
            print(f"MQTT Payload from actuator: {actuator_state}")

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
    ],
        style={
        'display': 'flex',
        'width' : '100%',
        'alignItems': 'center',
        'justifyContent': 'center',
        'textAlign': 'center',
        'height': '100px'
    }
    )


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


# Helper for styling cards
def card_style(flex=1, width='100%'):
    return {
        'flex': flex,
        'width': width,
        'padding': '15px',
        'backgroundColor': '#ffffff',
        'borderRadius': '15px',
        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
        'marginBottom': '20px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    }



def column_style():
    return {
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'space-between',
        'width': '30%',
        'minHeight': '650px'
    }

def row_style():
    return {
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'space-between',
        'alignItems': 'stretch',
        # 'width': '100%',
        'gap': '20px',
        'marginBottom': '20px',
        'width' : '210%'
    }


app.layout = html.Div([
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
        html.Div([
            html.Button("Download Data", id="download-button", n_clicks=0, style={
                'position': 'absolute',
                'top': '35px',
                'right': '30px',
                'padding': '10px 20px',
                'fontSize': '16px',
                'backgroundColor': '#0074D9',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer'
            }),
            dcc.Download(id="download-data")
        ]),

        # html.Img(
        #     src="https://img.icons8.com/?size=100&id=FNHbyJNFRRf4&format=png&color=000000",
        #     style={'height': '60px', 'marginLeft': '20px'}
        # ),
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'marginBottom': '30px'
    }),

    # First Row
    html.Div([
        # Outside Weather
        html.Div([
            html.Div([
                html.H3("Outside Weather", style={'textAlign': 'center', 'fontSize': '32px'}),
                labeled_box("https://img.icons8.com/color/70/thermometer.png", 'outside-temp-display'),
                labeled_box("https://img.icons8.com/color/70/hygrometer.png", 'outside-humidity-display'),
            ], style=card_style(flex=1)),
            html.Div([
                html.H3("Actuator Status", style={'textAlign': 'center', 'fontSize': '32px'}),
                labeled_box("https://img.icons8.com/color/70/fan.png", 'fan-speed-display'),
                labeled_box("https://img.icons8.com/color/70/conference-call.png", 'seats-display'),
                labeled_box("https://img.icons8.com/color/70/desk-lamp.png", 'indoor-light-status-display')
            ], style=card_style(flex=1))
        ], style=column_style()),

        # Current Plan
        html.Div([
            html.Div([
            html.Div([
                # html.H3("Current Plan", style={'textAlign': 'center', 'fontSize': '32px'}),
                html.Div(id='plan-display', style={'marginTop': '15px'})
            ], style=card_style(flex=1)),
            html.Div([
                html.H3("Interior Atmosphere", style={'textAlign': 'center', 'fontSize': '32px'}),
                labeled_box("https://img.icons8.com/color/70/temperature--v1.png", 'temp-display'),
                labeled_box("https://img.icons8.com/color/70/hygrometer.png", 'humidity-display'),
                labeled_box("https://img.icons8.com/color/70/light-on.png", 'indoor-light-level-display'),
                labeled_box("https://img.icons8.com/color/70/speaker.png", 'noise-display')
            ], style=card_style(flex=1))

            ], style = row_style()),
        #     html.Div([
        #     # html.H3("Mold Risk", style={'textAlign': 'center', 'fontSize': '32px'}),
        #     labeled_box("https://img.icons8.com/color/70/warning-shield.png", 'mold-risk-display')
        # ], style={**card_style(width='205%')})
            html.Div(id='mold-div',children = [
            # html.H3("Mold Risk", style={'textAlign': 'center', 'fontSize': '32px'}),
            labeled_box("https://img.icons8.com/color/70/warning-shield.png", 'mold-risk-display')
        ], style={ 'flex': 1,
        'padding': '15px',
        'backgroundColor': '#ffffff',
        'borderRadius': '15px',
        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
        'marginBottom': '20px',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'width' :'205%'})


        ], style=column_style()),

        # Inside Weather
        html.Div([

        ], style=column_style()),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'alignItems': 'stretch',
        'marginBottom': '20px',
        'gap': '20px'
    }),

    # Mold Risk spanning beneath Current Plan + Actuator Status
    html.Div([

    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'stretch',
        'marginBottom': '30px'
    }),

    # Seat Alert
    html.Div([
        html.Div(
            id='seat-alert-popup',
            children="Vacant seats available!",
            style={
                'position': 'fixed',
                'bottom': '20px',
                'right': '20px',
                'zIndex': '1000',
                'backgroundColor': '#ffcccc',
                'color': '#900',
                'padding': '15px 25px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.2)',
                'fontWeight': 'bold',
                'display': 'none',
            }
        )]),
    # }),

    dcc.Interval(id='interval-update', interval=3000, n_intervals=0)
], style={
    'backgroundColor': '#e4f2f7',
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
     Output('mold-risk-display', 'children'),
     Output('plan-display', 'children')],
    [Input('interval-update', 'n_intervals')]
)

def update_dashboard(n):
    # print(sensor_state)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    timestamps.append(now)
    temperature_data.append(sensor_state['inside_temperature'])
    noise_data.append(sensor_state['sound'])

    fan_speed_div = battery_indicator("Fan Speed", actuator_state['fan_speed'], max_level=3, color="#4caf50")

    indoor_light_div = battery_indicator("Indoor Light", actuator_state['light_level'], max_level=3,
                                         color="#ffc107")
    # vacancy = 1 if actuator_state['occupied'] == False else 0
    vacancy = 0 if sensor_state['ultrasonic']<=20 else 1

    temp_fig = go.Figure(go.Scatter(x=list(timestamps), y=list(temperature_data), mode='lines+markers'))
    temp_fig.update_layout(title='Temperature Over Time', xaxis_title='Time', yaxis_title='°C',
                           plot_bgcolor='#fefefe', paper_bgcolor='#ffffff')

    plan_html = [html.H3("Current Plan", style={'textAlign': 'center', 'fontSize': '32px'})]
    # for i, instr in enumerate(plan_instructions, start=1):
    #     plan_html.append(html.Div(f"{i}. {instr}", style={'fontSize':'25px','marginBottom': '5px', 'fontWeight': 'bold'}))
    for i, instr in enumerate(plan_instructions, start=1):
        plan_html.append(
            html.Div(
                f"{i}. {instr}",
                style={
                    'fontSize': '25px',
                    'marginBottom': '20px',  # Increased bottom space
                    'fontWeight': 'bold'
                }
            )
        )

    return (
        f"Temperature: {sensor_state['inside_temperature']} °C",
        f"Humidity: {sensor_state['inside_humidity']} %",
        f"LDR Reading: {sensor_state['raw_light']}",
        f"Temperature: {sensor_state['outside_temperature']} °C",
        f"Humidity: {sensor_state['outside_humidity']} %",
        f"Noise Level: {actuator_state['sound_level']}",
        fan_speed_div,
        indoor_light_div,
        f"Vacant Seats: {vacancy}",
        f"Mold Risk: {sensor_state['mold_risk_level']}",
        plan_html
    )

@app.callback(
    Output('seat-alert-popup', 'style'),
    Input('interval-update', 'n_intervals'),  # Or whatever Input you use to poll
    State('seats-display', 'children')        # Assuming this gets updated with the count
)
def toggle_popup(n, seat_info):
    try:
        vacant = int(seat_info.split()[-1])  # e.g., "Vacant Seats: 0"
        if vacant == 1:
            return {
                'position': 'fixed',
                'bottom': '20px',
                'right': '20px',
                'zIndex': '1000',
                'backgroundColor': '#ffcccc',
                'color': '#900',
                'padding': '15px 25px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.2)',
                'fontWeight': 'bold',
                'display': 'block',
            }
    except:
        pass
    return {'display': 'none'}

@app.callback(
    Output('mold-div', 'style'),
    Input('interval-update', 'n_intervals')  # Simulate sensor check/update
)
def update_mold_card_style(n):
    if sensor_state['mold_risk_level'] == 'HIGH':
        bg_colour_mold = '#FF9793'
    elif sensor_state['mold_risk_level'] == 'MEDIUM':
        bg_colour_mold = '#FFFFC5'
    elif sensor_state['mold_risk_level'] == 'LOW':
        bg_colour_mold = '#e6ffe6'

    # Merge background color into base style
    return {
        'flex': 1,
        'padding': '15px',
        'borderRadius': '15px',
        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.08)',
        'marginBottom': '20px',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'width' :'205%',
        'backgroundColor': bg_colour_mold,
        }




@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True
)
def generate_excel(n_clicks):
    try:
        # Combine sensor and actuator data
        combined_data = {
            "Parameter": list(sensor_state.keys()) + list(actuator_state.keys()),
            "Value": list(sensor_state.values()) + list(actuator_state.values())
        }

        df = pd.DataFrame(combined_data)

        # Save to Excel in-memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='SmartLibraryData')

        output.seek(0)

        return dcc.send_bytes(output.read(), filename="smart_library_data.xlsx")
    except Exception as e:
        print("Error generating Excel:", e)
        return None


if __name__ == '__main__':
    app.run(debug=True)