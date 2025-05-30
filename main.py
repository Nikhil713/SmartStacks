from multiprocessing import Process
import hardwareUtilities as hU
import sys
#import schedule


# ---- Parallel Process Launch ---- #
if __name__ == '__main__':
    p1 = Process(target=hU.ldr_led)
    # p2 = Process(target=hU.sound_oled)
    p3 = Process(target=hU.run_temperature_control_loop)
    # p3 = Process(target=read_light)

    p1.start()
    # p2.start()
    p3.start()
    # p3.start()

    try:
        p1.join()
        # p2.join()
        p3.join()
        # p3.join()

    except KeyboardInterrupt:
        print("Main process interrupted - Terminating child process")
        p1.terminate()
        # p2.terminate()
        p3.terminate()
        p1.join()
        # p2.join()
        p3.join()
        sys.exit(0)
        set_fan_speed(0)  # Turn off fan on exit




