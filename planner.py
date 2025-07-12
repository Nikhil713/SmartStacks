import math
import subprocess

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

from mqtt.mqtt_client import mqtt_callback
from logger import log

import requests

def get_sensor_data_and_create_problem_file():
    print("Inside sensor data code")

    # Light
    raw_light, intensity = read_ldr()
    print("Inside sensor data code 1")
    # Temp and Humidity
    temp, humidity = 27,65
    print("Inside sensor data code 2")
    # ultrasonic
    distance = read_ultrasonic()
    print("Inside sensor data code 3")
    # sound
    sound_value = get_random_sound_value()
    print("Inside sensor data code 4")
    # Temp/Humidity from weather api
    api_temp, api_humidity = get_weather()
    print("Inside sensor data code 5")
    # Mold risk - compound sensor
    # risk, mold_risk_level = 1,2
    risk, mold_risk_level = check_mold_risk(temp, humidity, api_temp, api_humidity)
    print("Inside sensor data code 6")
    
    #Sensor data
    sensor_data= {
        'inside_temperature': temp,
        'inside_humidity': humidity,
        'raw_light': raw_light,
        'ultrasonic': distance,
        'sound': sound_value,
        'outside_temperature': api_temp,
        'outside_humidity': api_humidity,
        'mold_risk_level': mold_risk_level
    }
    print("Going to send mqtt")
    mqtt_callback(sensor_data, "smartstacks/sensors")
    
    if not (math.isnan(temp) or math.isnan(humidity)):
        print("Going to send to planner")
        print(temp, humidity, raw_light, sound_value, mold_risk_level, distance)
        write_problem_pddl(temp, humidity, raw_light, sound_value, mold_risk_level, distance)



def write_problem_pddl(temp, humidity, raw_light, sound_value, mold_risk_level, distance):
    filepath = 'ai_planning/problem.pddl'

    goal = """
        (and
            (comfortable-lighting)
            (comfortable-temph)
            (comfortable-noise-level)
        )
    """ if (distance <20) else """
        (and
            (mold-risk-low)
        )
    """

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
        {goal}
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
    print("Goal written to problem.pddl:", goal.strip())

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

    # CMD way
    # cmd = [
    #     './fast-downward.py',
    #     domain,
    #     problem,
    #     '--search', 'lazy_greedy([ff()], preferred=[ff()])'
    # ]

    # try:
    #     result = subprocess.run(cmd, cwd='/home/pi/downward',
    #                             capture_output=True, text=True, timeout=30)
    #     output = result.stdout
    #     print("Planner Output:\n", output)

    #     if 'Solution found' in output:
    #         return output
    #     else:
    #         return None
    # except Exception as e:
    #     print(f"Error running planner: {e}")
    #     return None

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
    proper_actions = ["adjust-light-to-level-three","adjust-light-to-level-two","adjust-light-to-level-one","turn-on-light-to-level-one-very-dark","turn-on-light-to-level-one-dark","turn-off-light","alert-in-lcd-for-noise-level"]
    mqtt_plan = []
    for action_name in parsed_plan:
        if action_name in proper_actions:
            # print(f"Executing action: {action_name}")
            execute_actions(action_name)
            mqtt_plan.append(action_name)
    print(f"MQTT plan : {mqtt_plan}")
    
    

def execute_actions(action_name):
    if action_name == "adjust-light-to-level-three":
        pwm = set_led(3)
    elif action_name == "adjust-light-to-level-two":
        pwm = set_led(3)
    elif action_name == "turn-on-light-to-level-one-very-dark" or "turn-on-light-to-level-one-dark" or "adjust-light-to-level-one":
        pwm = set_led(3)
    elif action_name == "turn-off-light":
        pwm = set_led(0)

    # elif action_name == "turn-on-fan":
    #     control_fan_based_on_temperature(force_on=True)

    # elif action_name == "turn-off-fan":
    #     control_fan_based_on_temperature(force_on=False)

    # elif action_name == "display-message":
    #     message = " ".join(args)
    #     display_message(message)

    # elif action_name == "alert-in-lcd-for-noise-level":
    #     display_message("Too loud!")

    # Extend with more actions
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
        log(f"Planner error: {e}")
    
    # Sleep or wait for next iteration
    # time.sleep(5)  # Adjust as needed

        
