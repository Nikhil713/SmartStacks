import paho.mqtt.client as mqtt
import time
import json
# from hardware.sensor.LDR import read_ldr
# from hardware.actuator.LED import set_led
# from hardware.actuator.LCD_Display import *
# from hardware.sensor.temperature import read_temperature
# from hardware.actuator.fan import control_fan_based_on_temperature
# from hardware.sensor.pir import read_pir
# from hardware.sensor.ultrasonic import read_ultrasonic
# from software import weather_api
# from software.sensor import soundSensorSimulated


# raw_light = read_ldr()
# temp, humidity = read_temperature()
# distance = read_ultrasonic()
# sound_value = soundSensorSimulated.get_random_sound_value()
# api_temp, api_humidity= weather_api.get_weather()

# actuator_data= {
#     'inside_temperature': temp,
#     'inside_humidity': humidity,
#     'raw_light': raw_light,
#     'ultrasonic': distance,
#     'sound': sound_value,
#     'outside_temperature': api_temp,
#     'outside_humidity': api_humidity
# }


# MQTT config
BROKER = "test.mosquitto.org"          # or your broker’s IP/hostname
PORT = 1883
CLIENT_ID = "raspberrypi_sensor_01"    # unique identifier
# TOPIC = "smartstacks/sensors"

# TOPIC_SENSORS = "smartstacks/sensors"
# TOPIC_ACTUATORS = "smartstacks/actuators"
# TOPIC_PLAN = "smartstacks/plan"

mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.connect(BROKER, PORT, 60)

def mqtt_callback(data, TOPIC):

      payload = json.dumps(data)
      mqtt_client.publish(TOPIC, payload)
      print(f"Published → {payload}")
      time.sleep(5)
