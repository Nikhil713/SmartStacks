import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

pwm_pin = 18  # GPIO18 (physical pin 12)
GPIO.setup(pwm_pin, GPIO.OUT)

pwm = GPIO.PWM(pwm_pin, 1000)  # 1kHz frequency
pwm.start(0)  # Start at 0% duty cycle

try:
    print("Duty Cycle: 0%")
    pwm.ChangeDutyCycle(0)
    time.sleep(2)

    print("Duty Cycle: 50%")
    pwm.ChangeDutyCycle(50)
    time.sleep(2)

    print("Duty Cycle: 100%")
    pwm.ChangeDutyCycle(100)
    time.sleep(2)

finally:
    pwm.stop()
    GPIO.cleanup()
