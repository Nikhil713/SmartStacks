import time
from logger import log
from datetime import datetime
from software.sensor.soundSensorSimulated import get_random_sound_value
from hardware.actuator.LCD_Display import *
from mqtt.mqtt_client import mqtt_callback


def sound_lcd():
    try:
        while True:
            print("sensor_value in hu")
            # Sound Sensor + OLED
            sound_value, sound_level = get_random_sound_value()
            print(sound_value)
            msg = f"Sound: {sound_level}"
            setRGB(0,128,64)
            setText(msg)
            # mqtt_callback(msg)
            setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # mqtt_callback(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            log(msg)
            time.sleep(5)
            # for c in range(0,255):
            #     setText_norefresh("Going to sleep in {}...".format(str(c)))
            #     setRGB(c,255-c,0)
            #     time.sleep(0.1)
            setRGB(255,0,0)
            print(f"[Sound] Raw: {sound_value}, Level: {sound_level}")
            # setText("Bye bye, this should wrap onto next line")
            # time.sleep(5)

    except KeyboardInterrupt:
        print("Sound-OLED process interrupted")