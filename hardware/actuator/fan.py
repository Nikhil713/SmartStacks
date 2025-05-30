import grovepi
import time

# ------------ Configuration ------------
TEMP_SENSOR = 0  # A0 port for temperature sensor (DHT11)
FAN_SPEED_PINS = [3, 4, 5]  # D3, D4, D5 control fan speed levels 1-3

# ------------ Setup Functions ------------
def setup_fan_pins():
    """Initialize fan control pins."""
    for pin in FAN_SPEED_PINS:
        grovepi.pinMode(pin, "OUTPUT")

def initialize():
    """Run initial setup for all components."""
    setup_fan_pins()

# ------------ Fan Control Logic ------------
def set_fan_speed(speed):
    """
    Set fan speed (0–3). Higher speed turns on more pins.
    Speed 0 = fan off.
    """
    print(f"[FAN] Setting speed to {speed}")
    for i, pin in enumerate(FAN_SPEED_PINS):
        grovepi.digitalWrite(pin, 1 if i < speed else 0)

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

# ------------ Control Logic ------------
def control_fan_based_on_temperature(temp):
    """
    Decide and set fan speed based on temperature.
    """
    if temp is None:
        print("[TEMP] Invalid temperature reading.")
        return

    print(f"[TEMP] Current temperature: {temp}°C")

    if temp <= 20:
        set_fan_speed(0)
    elif 21 <= temp <= 23:
        set_fan_speed(1)
    elif 24 <= temp <= 26:
        set_fan_speed(2)
    else:
        set_fan_speed(3)

# ------------ Main Loop ------------
def run_temperature_control_loop():
    """Main loop to monitor temperature and control fan."""
    while True:
        temp = read_temperature()
        control_fan_based_on_temperature(temp)
        time.sleep(10)

# ------------ Entry Point ------------
if __name__ == "__main__":
    try:
        initialize()
        run_temperature_control_loop()
    except KeyboardInterrupt:
        print("\n[MAIN] Program stopped by user.")
        set_fan_speed(0)  # Turn off fan on exit
