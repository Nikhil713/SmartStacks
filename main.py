# from multiprocessing import Process
from threading import Thread, Event
import hardwareUtilities as hU
import softwareUtilities as sU
import planner as planner
import sys
# from hardware.actuator.fan import set_fan_speed
from hardware.actuator.LED import set_led
from hardware.actuator.LCD_Display import *
#import schedule
from logger import log

# Create a shared stop signal
stop_event = Event()

# ---- Parallel Process Launch ---- #
if __name__ == '__main__':
    # p1 = Process(target=hU.ldr_led)
    # p2 = Process(target=hU.sound_lcd)
    # p3 = Process(target=hU.run_temperature_control_loop)
    # p4 = Process(target=hU.run_pir_monitor_loop)

    p1 = Thread(target=hU.ldr_led)
    # p2 = Thread(target=sU.sound_lcd)
    # p3 = Thread(target=hU.run_temperature_control_loop)
    # p4 = Thread(target=hU.run_ultrasonic_monitor_loop)
    # p5 = Thread(target=sU.mold_prediction)
    planner_thread = Thread(target=planner.run_planner)

    p1.start()
    # p2.start()
    # p3.start()
    # p4.start()
    # p5.start()
    planner_thread.start()

    try:
        p1.join()
        # p2.join()
        # p3.join()
        # p4.join()
        # p5.join()
        planner_thread.join()



    except KeyboardInterrupt:
        log("Main process interrupted - Terminating child process")
        print("Main process interrupted - Terminating child process")
        stop_event.set()  # Signal all threads to stop
        # p1.terminate()
        # p2.terminate()
        # p3.terminate()
        # p4.terminate()
        # p1.join()
        # p2.join()
        # p3.join()
        # set_fan_speed(0)  # Turn off fan on exit
        setRGB(0, 0, 0)
        setText("")
        set_led(0)
        sys.exit(0)
