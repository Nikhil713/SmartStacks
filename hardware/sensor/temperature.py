import grovepi
import time

# ------------ Configuration ------------
TEMP_SENSOR = 2  # A2 port for temperature sensor (DHT11)


# ------------ Temperature Reading ------------
def read_temperature():
    try:
        temp, _ = grovepi.dht(TEMP_SENSOR, 2)  # 2 = DHT11
        return temp
    except Exception as e:
        print(f"[TEMP] Error: {e}")
        return None

# ------------ Control Logic ------------
def control_fan_based_on_temperature(temp):
    if temp is None:
        print("[TEMP] Invalid reading.")
        return

    print(f"[TEMP] Current temperature: {temp}°C")

    if temp <= 20:
        set_fan_pwm(0)
    elif 21 <= temp <= 23:
        set_fan_pwm(1)
    elif 24 <= temp <= 26:
        set_fan_pwm(2)
    else:
        set_fan_pwm(3)
