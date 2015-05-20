import threading
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(9, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)

GPIO.output(9, 0)
GPIO.output(11, 0)

gpio2 = False
gpio17 = False

def effet_boris():
    for i in range(1,6):
        GPIO.output(11, 0)
        GPIO.output(10, 1)
        time.sleep(0.2)
        GPIO.output(10, 0)
        GPIO.output(9, 1)
        time.sleep(0.2)
        GPIO.output(9, 0)
        GPIO.output(11, 1)
        time.sleep(0.2)
    GPIO.output(11, 0)
    GPIO.output(10, 1)
    

def blink(gpio, length):
    for i in range(1,length):
        GPIO.output(gpio, 1)
        time.sleep(0.3)
        GPIO.output(gpio, 0)
        time.sleep(0.3)


try:
    while True:
        if GPIO.input(22):
            print "Demo"
            threading.Thread(target=blink, args=(9, 10)).start()
        if GPIO.input(4):
            print "Call"
        if GPIO.input(17):
            print "Start"
            threading.Thread(target=blink, args=(11, 6)).start()
            #GPIO.output(11, 1)
        if GPIO.input(27):
            print "Stop"
            GPIO.output(11, 0)
        if GPIO.input(18) and not gpio2:
            print "Starting"
            gpio2 = True
            threading.Thread(target=effet_boris).start()
        if not GPIO.input(18) and gpio2:
            print "Stopping"
            gpio2 = False
            GPIO.output(10, 0)
        time.sleep(0.1)
finally:
    GPIO.cleanup()
