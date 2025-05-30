import grovepi

# Connect the Grove Light Sensor to analog port A0
# SIG,NC,VCC,GND
ldr_pin = 0
grovepi.pinMode(ldr_pin, "INPUT")


def read_ldr():
    try:
        value = grovepi.analogRead(ldr_pin)

        # Convert to intensity: 0 (dark) to 3 (bright)
        if value < 200:
            intensity = 0
        elif value < 500:
            intensity = 1
        elif value < 800:
            intensity = 2
        else:
            intensity = 3
        return value, intensity
    
    # Print "Error" if communication error encountered
    except IOError:				
        print ("Error")
