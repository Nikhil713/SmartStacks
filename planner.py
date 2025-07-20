import math
import subprocess
from logger import log

from hardware.sensor.LDR import read_ldr
from hardware.actuator.LED import set_led

from hardware.sensor.soundSensor import get_random_sound_value
from hardware.actuator.LCD_Display import *

from hardware.sensor.temperature import read_temperature
from hardware.actuator.fan import control_fan_based_on_temperature

from hardware.sensor.pir import read_pir
from hardware.sensor.ultrasonic import read_ultrasonic

from software.weather_api import get_weather

from software.mold_risk import check_mold_risk
from hardware.actuator.LCD_Display import *
from software.actuators.email import send_email_alert

from mqtt.mqtt_client import mqtt_callback


import requests

def get_sensor_data_and_create_problem_file():
    print("Inside sensor data code")

    # Light
    raw_light, intensity = read_ldr()
    # Temp and Humidity
    temp, humidity = read_temperature()
    # ultrasonic
    distance = read_ultrasonic()
    # sound
    sound_value = get_random_sound_value()
    # Temp/Humidity from weather api
    api_temp, api_humidity = get_weather()
    # Mold risk - compound sensor
    # risk, mold_risk_level = 1,2
    risk, mold_risk_level = check_mold_risk(temp, humidity, api_temp, api_humidity)
    #Sensor data
    sensor_data= {
        'inside_temperature': temp,
        'inside_humidity': humidity,
        'raw_light': raw_light,
        'ultrasonic': distance,
        'sound': sound_value,
        'outside_temperature': api_temp,
        'outside_humidity': api_humidity,
        'mold_risk_level': risk
    }
    print("Going to send mqtt")
    mqtt_callback(sensor_data, "smartstacks/sensors")
    
    if not (math.isnan(temp) or math.isnan(humidity)):
        print("Going to send to planner")
        print(temp, humidity, raw_light, sound_value, mold_risk_level, distance)
        write_problem_pddl(temp, humidity, raw_light, sound_value, mold_risk_level, distance)

    if (math.isnan(temp)):
        log("Error: Temp is NaN")

    if (math.isnan(humidity)):
        log("Error: Humidity is NaN")

    if (math.isnan(raw_light)):
        log("Error: Light is NaN")

    if (math.isnan(sound_value)):
        log("Error: Sound is NaN")

    if (math.isnan(mold_risk_level)):
        log("Error: Mold Risk is NaN")

    if (math.isnan(distance)):
        log("Error: Distance is NaN")

def write_problem_pddl(temp, humidity, raw_light, sound_value, mold_risk_level, distance):
    filepath = 'ai_planning/problem.pddl'

    with open(filepath, 'w') as f:
        f.write(f"""
(define (problem smart-library)
    (:domain environment-control)
    (:objects
        room - location
    )
    (:init
        (= (temperature room) {temp})
        (= (humidity room) {humidity})
        (= (light-level room) {raw_light})
        (= (sound-level room) {sound_value})
        (= (mold-risk room) {mold_risk_level})
        (= (ultrasonic-distance room) {distance})
    )
    (:goal
        (and
            (ideal-env)
        )
    )
)
""")
        
    print("Numeric values written to problem.pddl:")
    print(f"  temperature: {temp}")
    print(f"  humidity: {humidity}")
    print(f"  light level: {raw_light}")
    print(f"  sound level: {sound_value}")
    print(f"  mold risk: {mold_risk_level}")
    print(f"  distance: {distance}")

def send_pddl_files_and_get_plan(domain_file_path, problem_file_path):
    server_url='http://127.0.0.1:5000/plan'
    try:
        with open(domain_file_path, 'rb') as domain_file, open(problem_file_path, 'rb') as problem_file:
            files = {
                'domain': domain_file,
                'problem': problem_file
            }
            response = requests.post(server_url, files=files)
        
        response.raise_for_status()  # Raise error for HTTP failure

        data = response.json()
        full_output = data.get("plan", [])
        # print("Full planner output:", full_output)
        plan_steps = []
        # Extract only plan steps (ignore log lines)
        plan_steps = [line for line in full_output if not any(keyword in line.lower() for keyword in [
            "normalizing", "instantiating", "generating", "building", "translating", 
            "writing", "done", "cpu", "wall-clock", "axiom", "mutex", "fact", "group", "queue", "removed"
        ]) and line.strip()]

        return plan_steps

    except requests.exceptions.RequestException as e:
        print("Error sending PDDL files:", e)
        return []

def extract_plan_lines(planner_output):
    plan_lines = []

    for line in planner_output:
        stripped = line.strip().lower()

        if not stripped:
            continue
        if any(stripped.startswith(prefix) for prefix in [
            'normalizing', 'instantiating', 'generating', 'computing',
            'building', 'processing', 'detecting', 'reordering',
            'translator', 'done', 'remove', 'writing'
        ]):
            continue
        if any(kw in stripped for kw in ['cpu', 'wall-clock', 'mutex', 'axiom', 'proposition']):
            continue

        # Accept plan lines like "0: ACTION ARGS"
        if stripped[0].isdigit() and ':' in stripped:
            plan_lines.append(line.strip())

    return plan_lines


def parse_plan_response(plan_lines):
    parsed_plan = []

    for line in plan_lines:
        line = line.strip()
        if not line or line.startswith(";"):
            continue

        # Remove step number prefix if present (e.g., "1: ACTION ARGS")
        if ':' in line:
            line = line.split(':', 1)[1].strip()

        # Standardize case (optional — remove `.lower()` if you want case preserved)
        line = line.lower()

        # Parse action and arguments
        if '(' in line and ')' in line:
            action = line.split('(')[0].strip()
            args = line[line.find('(') + 1:line.find(')')].split()
        else:
            parts = line.split()
            if not parts:
                continue
            action = parts[0]
            args = parts[1:]

        parsed_plan.append(action)

    return parsed_plan



def execute_plan(parsed_plan):
    proper_actions = ["adjust-light-to-level-three",
                      "adjust-light-to-level-two",
                      "adjust-light-to-level-one",
                      "turn-on-light-to-level-one-very-dark",
                      "turn-on-light-to-level-one-dark",
                      "turn-off-light",
                      "turn-on-fan-to-level-three",
                      "turn-on-fan-to-level-two",
                      "turn-on-fan-to-level-one",
                      "turn-on-fan-to-reduce-humidity",
                      "turn-off-fan",
                      "display-quiet-in-lcd-display",
                      "display-normal-in-lcd-display",
                      "display-loud-in-lcd-display",
                      "turn-off-lcd-display",
                      "display-seat-occupied",
                      "send-email-for-high-mold-index"
                      ]
    mqtt_plan = []
    actuator_data = {}
    for action_name in parsed_plan:
        if action_name in proper_actions:
            # print(f"Executing action: {action_name}")
            execute_actions(action_name, actuator_data)
            mqtt_plan.append(action_name)
    # print(f"MQTT plan : {mqtt_plan}")
    mqtt_callback(mqtt_plan, "smartstacks/plan")
        
    # Also handle how to send actutator status to MQTT broker
    print(f"Actuator : {actuator_data}")
    mqtt_callback(actuator_data, "smartstacks/actuators")
    
    

def execute_actions(action_name, actuator_data):
    if action_name == "adjust-light-to-level-three":
        print(f"Executing action: {action_name}")
        set_led(3)
        actuator_data['light_level'] = 3
    elif action_name == "adjust-light-to-level-two":
        print(f"Executing action: {action_name}")
        set_led(2)
        actuator_data['light_level'] = 2
    elif action_name in ["turn-on-light-to-level-one-very-dark", "turn-on-light-to-level-one-dark", "adjust-light-to-level-one"]:
        set_led(1)
        print(f"Executing action: {action_name}")
        actuator_data['light_level'] = 1
    elif action_name == "turn-off-light":
        set_led(0)
        print(f"Executing action: {action_name}")
        actuator_data['light_level'] = 0

    elif action_name == "turn-on-fan-to-level-three":
        print(f"Executing action: {action_name}")
        actuator_data['fan_speed'] = 3
    elif action_name == "turn-on-fan-to-level-two":
        print(f"Executing action: {action_name}")
        actuator_data['fan_speed'] = 2
    elif action_name == "turn-on-fan-to-level-one":
        print(f"Executing action: {action_name}")
        actuator_data['fan_speed'] = 1
    elif action_name == "turn-on-fan-to-reduce-humidity":
        actuator_data['fan_speed'] = 3
        print(f"Executing action: {action_name}")
    elif action_name == "turn-off-fan":
        print(f"Executing action: {action_name}")
        actuator_data['fan_speed'] = 0

    elif action_name == "display-quiet-in-lcd-display":
        print(f"Executing action: {action_name}")
        setRGB(0,255,0)
        actuator_data['sound_level'] = "Quiet"
        sound_level = "Quiet"
        setText(sound_level)
        
    elif action_name == "display-normal-in-lcd-display":
        print(f"Executing action: {action_name}")
        setRGB(125,125,125)
        sound_level = "Normal"
        actuator_data['sound_level'] = "Normal"
        setText(sound_level)
    elif action_name == "display-loud-in-lcd-display":
        print(f"Executing action: {action_name}")
        setRGB(255,0,0)
        sound_level = "Loud"
        actuator_data['sound_level'] = "Loud"
        setText(sound_level)
    elif action_name == "turn-off-lcd-display":
        print(f"Executing action: {action_name}")
        setRGB(0, 0, 0)
        setText("")
        actuator_data['sound_level'] = "Off"
        
    elif action_name == "display-seat-occupied":
        print(f"Executing action: {action_name}")
        actuator_data['occupied'] = True
        
    elif action_name == "send-email-for-high-mold-index":
        print(f"Executing action: {action_name}")
        send_email_alert(
        subject=" Mold Risk Alert - High",
        body="Mold risk has reached a high level in the Smart Library. Immediate action is recommended!"
    )
    else:
        print(f"Unknown action: {action_name}")


def run_planner():
    
    try:
        while True:
            domain = 'ai_planning/domain.pddl'
            problem = 'ai_planning/problem.pddl'
            # Get sensor data and create problem file
            get_sensor_data_and_create_problem_file()

            # Send PDDL files and get plan
            
            planner_output = send_pddl_files_and_get_plan(domain, problem)

            if not planner_output:
                print("No plan recieved. Environment is in ideal conditions")
                time.sleep(5)
                continue

            plan_lines = extract_plan_lines(planner_output)
            parsed_plan = parse_plan_response(plan_lines)
            print("Actions to be performed:", parsed_plan)

            execute_plan(parsed_plan)
            time.sleep(5)

    except Exception as e:
        print(f"Planner error: {e}")
        log(f"Planner error: {e}")
    
    # Sleep or wait for next iteration
    # time.sleep(5)  # Adjust as needed

        
