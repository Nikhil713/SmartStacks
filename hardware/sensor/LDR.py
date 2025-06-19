import grovepi
from mqtt.mqtt_client import mqtt_callback

# Connect the Grove Light Sensor to analog port A0
# SIG,NC,VCC,GND
ldr_pin = 0
grovepi.pinMode(ldr_pin, "INPUT")


def read_ldr():
    try:
        value = grovepi.analogRead(ldr_pin)

        # Convert to intensity: 0 (dark) to 3 (bright)
        if value < 200:
            intensity = 3
        elif value < 500:
            intensity = 2
        elif value < 800:
            intensity = 1
        else:
            intensity = 0

        mqtt_callback(f"[LDR] Raw: {value}, Intensity: {intensity}")

        return value, intensity
    
    # Print "Error" if communication error encountered
    except IOError:				
        print ("Error")
