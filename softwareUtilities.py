import time
from logger import log
from datetime import datetime
from software.sensor.soundSensorSimulated import get_random_sound_value
from hardware.actuator.LCD_Display import *
from mqtt.mqtt_client import mqtt_callback
from software.mold_risk import *


def sound_lcd():
    try:
        while True:
            print("sensor_value in hu")
            # Sound Sensor + LCD Display
            sound_value = get_random_sound_value()
            print(sound_value)
            msg = f"Sound: {sound_value}"

            if sound_value < 100:
                setRGB(0,255,0)
                level = "Quiet"
                setText(level)
            elif sound_value < 200:
                setRGB(125,125,125)
                level = "Normal"
                setText(level)
            else:
                setRGB(255,0,0)
                level = "Loud"
                setText(level)

            # setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            log(msg)
            print(f"[Sound] Raw: {sound_value}")
            # setText("Bye bye, this should wrap onto next line")
            time.sleep(5)

    except KeyboardInterrupt:
        print("Sound-OLED process interrupted")


def mold_prediction():
    try:
        while True:
            int_temp, int_rh = read_temperature()

            if int_temp is None or int_rh is None:
                print("Failed to read internal data.")
                return

            ext_temp, ext_rh = get_weather()
            if ext_temp is None or ext_rh is None:
                print("Failed to get external data.")
                return

            risk, int_dp, ext_dp, checks = check_mold_risk(int_temp, int_rh, ext_temp, ext_rh)

            print("\n--- MOLD RISK ANALYSIS ---")
            print(f"Internal Temp: {int_temp:.1f}°C")
            print(f"Internal RH:   {int_rh:.1f}%")
            print(f"Internal DP:   {int_dp:.1f}°C")
            print(f"External Temp: {ext_temp:.1f}°C")
            print(f"External RH:   {ext_rh:.1f}%")
            print(f"External DP:   {ext_dp:.1f}°C\n")

            print(f"\n Mold Risk Level: {risk}")
            print("-----------------------------\n")

            # Log to CSV
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            data = [
                round(int_temp, 2), round(int_rh, 2), round(int_dp, 2),
                round(ext_temp, 2), round(ext_rh, 2), round(ext_dp, 2), risk
            ]
            log_to_csv(timestamp, data) 


    except KeyboardInterrupt:
        print("Mold_risk prediction failed")