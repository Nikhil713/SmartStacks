import grovepi

# Connect the Grove Sound Sensor to analog port A1
# SIG,NC,VCC,GND
sound_sensor = 1
grovepi.pinMode(sound_sensor,"INPUT")

def noiseLevel():
    try:
        # Read the sound level
        print("sensor_value")
        sensor_value = grovepi.analogRead(sound_sensor)
        print(sensor_value)
        if sensor_value < 100:
            level = "Quiet"
        elif sensor_value < 200:
            level = "Normal"
        else:
            level = "Loud"
        return sensor_value, level
    
    # Print "Error" if communication error encountered
    except IOError:				
        print ("Error")