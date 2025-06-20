import random
from mqtt.mqtt_client import mqtt_callback


def get_random_sound_value():

    """
    Returns a random integer simulating an analog sound sensor reading.
    
    Range: 0 (silent) to 1023 (loud)
    """

    try:
        sensor_value = random.randint(0, 1023)
        print(sensor_value)
        if sensor_value < 100:
            level = "Quiet"
        elif sensor_value < 200:
            level = "Normal"
        else:
            level = "Loud"
        mqtt_callback(f"[Sound] Raw: {sensor_value}, Level: {level}")

        return sensor_value, level
    
    # Print "Error" if communication error encountered
    except IOError:			
        print ("Error")
