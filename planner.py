import subprocess

from hardware.sensor.LDR import read_ldr
from hardware.actuator.LED import set_led

from hardware.sensor.soundSensor import noiseLevel
from hardware.actuator.LCD_Display import *

from hardware.sensor.temperature import read_temperature
from hardware.actuator.fan import control_fan_based_on_temperature

from hardware.sensor.pir import read_pir
from hardware.sensor.ultrasonic import read_ultrasonic

from software.weather_api import get_weather
from logger import log

import requests

def get_sensor_data_and_create_problem_file():
    raw_light, intensity = read_ldr()
    temp, humidity = read_temperature()
    distance = read_ultrasonic()
    sound_value, sound_level = noiseLevel()
    api_temp, api_humidity = get_weather()

    if distance < 20:
        occupied = True
    else:
        occupied = False
    write_problem_pddl(temp, humidity, intensity, sound_value, api_temp, api_humidity, occupied)



def write_problem_pddl(temp, humidity, light, sound, api_temp, api_humidity, occupied):
    filepath = 'ai_planning/problem.pddl'
    facts = []

    # Temperature classification
    if temp <= 20:
        facts.append("(temp-very-low)")
    elif temp <= 23:
        facts.append("(temp-low)")
    elif temp <= 26:
        facts.append("(temp-normal)")
    else:
        facts.append("(temp-high)")

    # Humidity
    if humidity > 70:
        facts.append("(high-humidity)")
    else:
        facts.append("(normal-humidity)")

    # Light
    if light <= 200:
        facts.append("(very-dark-light)")
    elif light <= 500:
        facts.append("(dark-light)")
    elif light <= 800:
        facts.append("(normal-light)")
    else:
        facts.append("(bright-light)")

    # Sound
    # if sound <= 100:
    #     facts.append("(quiet)")
    # elif sound <= 200:
    #     facts.append("(normal)")
    # else:
    #     facts.append("(loud)")

    # Occupancy
    facts.append("(seat-occupied)" if occupied else "(seat-empty)")

    goal = """
        (and
            (mold-risk-low)
            (comfortable)
        )
    """ if occupied else """
        (and
            (mold-risk-low)
            (energy-saved)
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
            {' '.join(facts)}
        )
        (:goal
            {goal}
        )
    )
    """)
        
    print("Facts written to problem.pddl:", facts)
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
        print("Full planner output:", full_output)
        plan_steps = []
        # Extract only plan steps (ignore log lines)
        # plan_steps = [line for line in full_output if not any(keyword in line.lower() for keyword in [
        #     "normalizing", "instantiating", "generating", "building", "translating", 
        #     "writing", "done", "cpu", "wall-clock", "axiom", "mutex", "fact", "group", "queue", "removed"
        # ]) and line.strip()]

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

def parse_plan_response(plan_lines):
    """
    Parses a list of plan steps like:
    ["turn-on (1)", "adjust-fan room high", ...]
    into a list of clean action tuples:
    [("turn-on", ["1"]), ("adjust-fan", ["room", "high"])]
    """
    parsed_plan = []

    for line in plan_lines:
        line = line.strip()

        if not line or line.startswith(";"):
            continue  # Skip comments or empty lines

        # Remove numbering if present (e.g., "1: turn-on room")
        if ':' in line:
            line = line.split(':', 1)[1].strip()

        # Extract action and parameters
        if '(' in line and ')' in line:
            action = line.split('(')[0].strip()
            args = line[line.find('(') + 1:line.find(')')].split()
        else:
            parts = line.split()
            action = parts[0]
            args = parts[1:]

        parsed_plan.append((action, args))

    return parsed_plan

def execute_plan(parsed_plan):
    for action_name, args in parsed_plan:
        print(f"Executing action: {action_name} with args {args}")
        execute_actions(action_name, args)

def execute_actions(action_name, args):
    if action_name == "max-light":
        set_led(3)  # Set LED to maximum brightness
    elif action_name == "great-light":
        set_led(2)  # Dim the LED
    elif action_name == "dim-light":
        set_led(2)  # Dim the LED
    elif action_name == "turn-off-light":
        set_led(0)

    # elif action_name == "turn-on-fan":
    #     control_fan_based_on_temperature(force_on=True)

    # elif action_name == "turn-off-fan":
    #     control_fan_based_on_temperature(force_on=False)

    # elif action_name == "display-message":
    #     message = " ".join(args)
    #     display_message(message)

    # elif action_name == "alert-noise":
    #     display_message("Too loud!")

    # Extend with more actions
    else:
        print(f"Unknown action: {action_name} with args {args}")

    

def run_planner():
    while True:
        try:
            domain = 'ai_planning/domain.pddl'
            problem = 'ai_planning/problem.pddl'
            # Get sensor data and create problem file
            get_sensor_data_and_create_problem_file()

            # Send PDDL files and get plan
            
            plan_response = send_pddl_files_and_get_plan(domain, problem)

            if not plan_response:
                print("No valid plan found.")
                continue

            parsed_plan = parse_plan_response(plan_response)
            print("Actions to be performed:", parsed_plan)

            execute_plan(parsed_plan)

        except Exception as e:
            log(f"Planner error: {e}")
        
        # Sleep or wait for next iteration
        # time.sleep(5)  # Adjust as needed

        
