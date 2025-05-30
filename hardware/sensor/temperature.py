import grovepi
import time

# ------------ Configuration ------------
TEMP_SENSOR = 2  # A2 port for temperature sensor (DHT11)


# ------------ Temperature Reading ------------
def read_temperature():
    try:
        temp, _ = grovepi.dht(TEMP_SENSOR, 2)  # 2 = DHT11
        print(f"Raw reading: temp={temp}, humidity={humidity}")
        return temp
    except Exception as e:
        print(f"[TEMP] Error: {e}")
        return None
