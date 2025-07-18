from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT configuration
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "device/logs"
CLIENT_ID = "raspberrypi_sensor_01" 


# Setup MQTT client once
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

LOG_FILE = "device_log.txt"  # Log file 

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "w") as f:
        f.write(entry)

        # Send via MQTT
        mqtt_client.publish(MQTT_TOPIC, entry)
    f.close()