import grovepi

# ------------ Configuration ------------
TEMP_SENSOR_PORT = 2  # A2 port for temperature sensor (DHT11)


# ------------ Temperature Reading ------------
def read_temperature():
    try:
        temp, humidity = grovepi.dht(TEMP_SENSOR_PORT, 0)  # 1 = DHT11
        print(f"Raw reading: temp={temp}, humidity={humidity}")
        return temp
    except Exception as e:
        print(f"[TEMP] Error: {e}")
        return None
