import grovepi
import time

# ------------ Configuration ------------
FAN_PWM_PIN = 6        # D6 - PWM-capable pin

# ------------ Setup ------------
def initialize():
    grovepi.pinMode(FAN_PWM_PIN, "OUTPUT")

# ------------ Fan Control with PWM ------------
def set_fan_pwm(speed_level):
    """
    Set fan speed using PWM.
    speed_level: 0 to 3
    """
    pwm_values = {
        0: 0,       # OFF
        1: 85,      # ~33% speed
        2: 170,     # ~66% speed
        3: 255      # Full speed
    }
    pwm = pwm_values.get(speed_level, 0)
    print(f"[FAN] Setting speed level {speed_level} (PWM: {pwm})")
    grovepi.analogWrite(FAN_PWM_PIN, pwm)


