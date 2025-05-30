import grovepi
import time

# ------------ Configuration ------------
TEMP_SENSOR = 0  # A0 port for temperature sensor (DHT11)


# ------------ Sensor Reading Logic ------------
def read_temperature():
    """
    Read temperature from DHT11 sensor.
    Returns: temperature in °C or None if read fails.
    """
    try:
        temp, _ = grovepi.dht(TEMP_SENSOR, 0)  # 0 = DHT11
        return temp
    except Exception as e:
        print(f"[TEMP] Error reading sensor: {e}")
        return None


# ------------ Main Loop ------------
def run_temperature_control_loop():
    """Main loop to monitor temperature and control fan."""
    while True:
        temp = read_temperature()
        control_fan_based_on_temperature(temp)
        time.sleep(2)

# ------------ Entry Point ------------
if __name__ == "__main__":
    try:
        initialize()
        run_temperature_control_loop()
    except KeyboardInterrupt:
        print("\n[MAIN] Program stopped by user.")
        set_fan_speed(0)  # Turn off fan on exit
