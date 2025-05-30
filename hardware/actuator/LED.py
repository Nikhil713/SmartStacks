import grovepi

#https://github.com/DexterInd/GrovePi

# Digital ports that support Pulse Width Modulation (PWM)
# D3, D5, D6

# Digital ports that do not support PWM
# D2, D4, D7, D8

# Connect the LED to digital port D4
# SIG,NC,VCC,GND
led_pin = 5
grovepi.pinMode(led_pin, "OUTPUT")

def set_led(intensity):
    pwm = {0: 0, 1: 64, 2: 128, 3: 255}.get(intensity, 0)

    try:
        grovepi.analogWrite(led_pin, pwm)
        return pwm
    
    # Turn LED off before stopping
    except KeyboardInterrupt:	
        grovepi.digitalWrite(led_pin,0)

    # Print "Error" if communication error encountered
    except IOError:				
        print ("Error")
