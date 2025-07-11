import time
from datetime import datetime
from hardware.sensor.LDR import read_ldr
from hardware.actuator.LED import set_led
from hardware.actuator.LCD_Display import *
from hardware.sensor.temperature import read_temperature
from hardware.actuator.fan import control_fan_based_on_temperature
from hardware.sensor.pir import read_pir
from hardware.sensor.ultrasonic import read_ultrasonic
from logger import log
from mqtt.mqtt_client import mqtt_callback

# ---- Sensor Read Functions ---- #

def ldr_led():
    try:
        while True:
            #LDR + LED
            raw, intensity = read_ldr()
            # pwm = set_led(intensity)
            ldr_msg = f"LDR raw={raw}, intensity={intensity}"
            # print(ldr_msg)
            log(ldr_msg)
            # mqtt_callback(ldr_msg)
            time.sleep(5)

    except KeyboardInterrupt:
        print("LDR-LED process interrupted")


# def sound_lcd():
#     try:
#         while True:
#             print("sensor_value in hu")
#             # Sound Sensor + OLED
#             sound_value, sound_level = noiseLevel()
#             print(sound_value)
#             msg = f"Sound: {sound_level}"
#             setRGB(0,128,64)
#             setText(msg)
#             setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#             log(msg)
#             time.sleep(5)
#             # for c in range(0,255):
#             #     setText_norefresh("Going to sleep in {}...".format(str(c)))
#             #     setRGB(c,255-c,0)
#             #     time.sleep(0.1)
#             setRGB(255,0,0)
#             print(f"[Sound] Raw: {sound_value}, Level: {sound_level}")
#             # setText("Bye bye, this should wrap onto next line")
#             # time.sleep(5)

#     except KeyboardInterrupt:
#         print("Sound-OLED process interrupted")


def run_temperature_control_loop():
    """Main loop to monitor temperature and control fan."""
    try:
        while True:
            temp, humidity = read_temperature()
            control_fan_based_on_temperature(temp)
            msgTemp = f"Raw reading: temp={temp}, humidity={humidity}"
            print(msgTemp)
            log(msgTemp)
            # mqtt_callback(msgTemp)
            time.sleep(5)

    except KeyboardInterrupt:
        print("Sound-OLED process interrupted")

def run_pir_monitor_loop():
    """
    Main loop to monitor PIR sensor and print vacancy status.
    """
    try:
        while True:
            vacant_seats = read_pir()
            if vacant_seats is not None:
                print(f"Vacant Seats: {vacant_seats}")
            # mqtt_callback(vacant_seats)
            time.sleep(5)

    except KeyboardInterrupt:
        print("PIR process interrupted")

def run_ultrasonic_monitor_loop():
    """
    Continuously monitors the ultrasonic sensor and prints seat vacancy status.
    """
    try:
        while True:
            vacant_seats = read_ultrasonic()
            if vacant_seats is not None:
                print(f"Vacant Seats: {vacant_seats}")
            # mqtt_callback(vacant_seats)
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("Ultrasonic process interrupted")