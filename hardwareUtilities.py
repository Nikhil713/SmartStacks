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