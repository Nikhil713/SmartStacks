import time
from hardware.sensor.LDR import read_ldr
from hardware.actuator.LED import set_led
from hardware.sensor.soundSensor import noiseLevel
from hardware.actuator.LED_Display import show_message
from hardware.sensor.temperature import read_temperature
from hardware.actuator.fan import control_fan_based_on_temperature
# ---- Sensor Read Functions ---- #

def ldr_led():
    try:
        while True:
            #LDR + LED
            raw, intensity = read_ldr()
            pwm = set_led(intensity)
            print(f"LDR raw: {raw}, Intensity: {intensity}, LED PWM: {pwm}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("LDR-LED process interrupted")


def sound_oled():
    try:
        while True:
            # Sound Sensor + OLED
            sound_value, sound_level = noiseLevel()
            msg = f"Sound: {sound_level}"
            show_message(msg)
            print(f"[Sound] Raw: {sound_value}, Level: {sound_level}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("SOund-OLED process interrupted")

# def read_light():
#     while True:
#         print("Reading Light sensor...")
#         time.sleep(5)

def run_temperature_control_loop():
    """Main loop to monitor temperature and control fan."""
    while True:
        temp = read_temperature()
        control_fan_based_on_temperature(temp)
        time.sleep(10)
