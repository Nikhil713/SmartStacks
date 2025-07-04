# LCD_Display.py
import smbus
import time
import threading
import sys

# Global I2C lock to prevent concurrent I2C access
i2c_lock = threading.Lock()

# I2C addresses for the Grove LCD
DISPLAY_TEXT_ADDR = 0x3e
DISPLAY_RGB_ADDR = 0x62

# Initialize I2C bus (1 for Raspberry Pi newer models)
if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)


def textCommand(cmd):
    """Send a command byte to the LCD."""
    for attempt in range(3):
        try:
            with i2c_lock:
                bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)
            break
        except OSError as e:
            print(f"[LCD] I2C error in textCommand (attempt {attempt+1}): {e}")
            time.sleep(0.1)

def setRGB(r, g, b):
    """Set the backlight color of the LCD."""
    for attempt in range(3):
        try:
            with i2c_lock:
                bus.write_byte_data(DISPLAY_RGB_ADDR, 0, 0)
                bus.write_byte_data(DISPLAY_RGB_ADDR, 1, 0)
                bus.write_byte_data(DISPLAY_RGB_ADDR, 0x08, 0xaa)
                bus.write_byte_data(DISPLAY_RGB_ADDR, 4, r)
                bus.write_byte_data(DISPLAY_RGB_ADDR, 3, g)
                bus.write_byte_data(DISPLAY_RGB_ADDR, 2, b)
            break
        except OSError as e:
            print(f"[LCD] I2C error in setRGB (attempt {attempt+1}): {e}")
            time.sleep(0.1)

def setText(text):
    """Clear screen and write text to the LCD (up to 2 lines)."""
    for attempt in range(3):
        try:
            with i2c_lock:
                textCommand(0x01)  # clear display
                time.sleep(0.05)
                textCommand(0x08 | 0x04)  # display on, no cursor
                textCommand(0x28)  # 2 lines
                time.sleep(0.05)

                count = 0
                row = 0
                for c in text:
                    if c == '\n' or count == 16:
                        count = 0
                        row += 1
                        if row == 2:
                            break
                        textCommand(0xc0)
                        if c == '\n':
                            continue
                    count += 1
                    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))
            break
        except OSError as e:
            print(f"[LCD] I2C error in setText (attempt {attempt+1}): {e}")
            time.sleep(0.1)

def setText_norefresh(text):
    """Write text to LCD without clearing screen (useful for fast updates)."""
    for attempt in range(3):
        try:
            with i2c_lock:
                textCommand(0x08 | 0x04)  # display on, no cursor
                textCommand(0x28)  # 2 lines
                time.sleep(0.05)

                count = 0
                row = 0
                for c in text:
                    if c == '\n' or count == 16:
                        count = 0
                        row += 1
                        if row == 2:
                            break
                        textCommand(0xc0)
                        if c == '\n':
                            continue
                    count += 1
                    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))
            break
        except OSError as e:
            print(f"[LCD] I2C error in setText_norefresh (attempt {attempt+1}): {e}")
            time.sleep(0.1)
