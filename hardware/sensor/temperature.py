import grovepi
from mqtt.mqtt_client import mqtt_callback

# ------------ Configuration ------------
TEMP_SENSOR_PORT = 4  # D4 port for temperature sensor (DHT11)


# ------------ Temperature Reading ------------
def read_temperature():
    try:
        temp, humidity = grovepi.dht(TEMP_SENSOR_PORT, 0)  # 0 = DHT11
        # mqtt_callback(f"[TEMP] Temp: {temp}, Humidity: {humidity}")
        return temp, humidity
    
    except Exception as e:
        print(f"[TEMP] Error: {e}")
        return None
