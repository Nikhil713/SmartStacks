import grovepi
import time

# ------------ Configuration ------------
PIR_SENSOR_PORT = 7 

def read_pir(pir_port):
    """
    Reads PIR sensor value.
    Returns 0 if motion detected (seat occupied), 1 if no motion (seat vacant).
    """
    grovepi.pinMode(PIR_SENSOR_PORT , "INPUT")
    try:
        pir_value = grovepi.digitalRead(PIR_SENSOR_PORT)
        return 0 if pir_value == 1 else 1
    except IOError:
        print("Error reading PIR sensor")
        return None