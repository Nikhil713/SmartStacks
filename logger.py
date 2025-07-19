from datetime import datetime
from mqtt_client import mqtt_file_send

# MQTT configuration

MQTT_TOPIC = "device/logs"
LOG_FILE = "device_log.txt"  # Log file

# mqtt_client = mqtt.Client(client_id=CLIENT_ID)
# mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "w") as f:
        f.write(entry)

        # Send via MQTT
        mqtt_file_send(MQTT_TOPIC, entry)
    f.close()