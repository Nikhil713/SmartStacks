# from multiprocessing import Process
from threading import Thread, Event
import hardwareUtilities as hU
import sys
#import schedule

# Create a shared stop signal
stop_event = Event()

# ---- Parallel Process Launch ---- #
if __name__ == '__main__':
    # p1 = Process(target=hU.ldr_led)
    # p2 = Process(target=hU.sound_oled)
    # p3 = Process(target=hU.run_temperature_control_loop)
    # p4 = Process(target=hU.run_pir_monitor_loop)

    p1 = Thread(target=hU.ldr_led)
    p2 = Thread(target=hU.sound_oled)
    p3 = Thread(target=hU.run_temperature_control_loop)
    p4 = Thread(target=hU.run_ultrasonic_monitor_loop)
    # p3 = Process(target=read_light)

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    try:
        p1.join()
        p2.join()
        p3.join()
        p4.join()

    except KeyboardInterrupt:
        print("Main process interrupted - Terminating child process")
        stop_event.set()  # Signal all threads to stop
        # p1.terminate()
        # p2.terminate()
        # p3.terminate()
        # p4.terminate()
        # p1.join()
        # p2.join()
        # p3.join()
        sys.exit(0)
        set_fan_speed(0)  # Turn off fan on exit




