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
        print("Sound-OLED process interrupted")