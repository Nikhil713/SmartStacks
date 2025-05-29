import grovepi
import time
port=4
sensor=0
timeout = 5
while True:
    [temperature,humidity] = grovepi.dht(port,sensor)
    print ("{} Temperature = {} C, humidity = {} %".format(time.ctime(),temperature,humidity))
    time.sleep(timeout)

#test push durga