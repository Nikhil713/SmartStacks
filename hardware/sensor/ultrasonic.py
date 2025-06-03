import grovepi

# --- Configuration ---
ULTRASONIC_PORT = 7          # Digital port D7
ULTRASONIC_THRESHOLD = 10    # Distance in cm

def read_ultrasonic():
    """
    Reads distance from the ultrasonic sensor.
    Returns 0 (occupied) if object is closer than threshold, 1 (vacant) otherwise.
    """
    try:
        distance = grovepi.ultrasonicRead(ULTRASONIC_PORT)
        print(f"Ultrasonic Distance: {distance} cm")
        return 0 if distance < ULTRASONIC_THRESHOLD else 1
    except IOError:
        print("Error reading ultrasonic sensor")
        return None
