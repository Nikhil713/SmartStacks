import random
from mqtt.mqtt_client import mqtt_callback
from logger import log


def get_random_sound_value():

    """
    Returns a random integer simulating an analog sound sensor reading.
    
    Range: 0 (silent) to 1023 (loud)
    """

    try:
        sensor_value = random.randint(0, 1023)
        # mqtt_callback(f"[Sound] Raw: {sensor_value}")

        return sensor_value
    
    # Print "Error" if communication error encountered
    except IOError:			
        print ("Error")
        log("[Sound] Error")
