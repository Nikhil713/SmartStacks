import paho.mqtt.client as mqtt
import time
import json

# MQTT config
BROKER = "test.mosquitto.org"          # or your broker’s IP/hostname
PORT = 1883
CLIENT_ID = "raspberrypi_sensor_01"    # unique identifier
TOPIC = "smartstacks/sensors"

mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.connect(BROKER, PORT, 60)

while True:
    # Data from sensors
    data = {
      "temperature": 25.3,
      "humidity": 60.2
    }

    payload = json.dumps(data)
    mqtt_client.publish(TOPIC, payload)
    print(f"Published → {payload}")
    time.sleep(5)
