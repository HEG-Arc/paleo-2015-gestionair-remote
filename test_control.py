import threading
import RPi.GPIO as GPIO
import time

BTN_KEY = 18
BTN_DEMO = 22
BTN_CALL = 4
BTN_START = 17
BTN_STOP = 27
LED_ON = 10
LED_DEMO = 9
LED_START = 11 

GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_KEY, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BTN_DEMO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BTN_CALL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BTN_START, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BTN_STOP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_ON, GPIO.OUT)
GPIO.setup(LED_DEMO, GPIO.OUT)
GPIO.setup(LED_START, GPIO.OUT)

GPIO.output(LED_ON, 0)
GPIO.output(LED_DEMO, 0)
GPIO.output(LED_START, 0)

btn_key_prev_reading = 0
btn_demo_prev_reading = 0
btn_call_prev_reading = 0
btn_start_prev_reading = 0
btn_stop_prev_reading = 0

def effet_boris():
    for i in range(1,6):
        GPIO.output(LED_START, 0)
        GPIO.output(LED_ON, 1)
        time.sleep(0.2)
        GPIO.output(LED_ON, 0)
        GPIO.output(LED_DEMO, 1)
        time.sleep(0.2)
        GPIO.output(LED_DEMO, 0)
        GPIO.output(LED_START, 1)
        time.sleep(0.2)
    GPIO.output(LED_START, 0)
    GPIO.output(LED_ON, 1)
    

def blink(led, length, end_on=False):
    for i in range(1,length):
        GPIO.output(led, 1)
        time.sleep(0.3)
        GPIO.output(led, 0)
        time.sleep(0.3)
    if end_on:
        GPIO.output(led, 1)


try:
    while True:
        # Button DEMO
        btn_demo_reading = GPIO.input(BTN_DEMO)
        if btn_demo_reading and not btn_demo_prev_reading:
            print "Demo"
            threading.Thread(target=blink, args=(LED_DEMO, 10, False)).start()
        btn_demo_prev_reading = btn_demo_reading

        # Button CALL
        btn_call_reading = GPIO.input(BTN_CALL)
        if btn_call_reading and not btn_call_prev_reading:
            print "Call"
        btn_call_prev_reading = btn_call_reading

        # Button START
        btn_start_reading = GPIO.input(BTN_START)
        if btn_start_reading and not btn_start_prev_reading:
            print "Start"
            threading.Thread(target=blink, args=(LED_START, 6, True)).start()
        btn_start_prev_reading = btn_start_reading

        # Button STOP
        btn_stop_reading = GPIO.input(BTN_STOP)
        if btn_stop_reading and not btn_stop_prev_reading:
            print "Stop"
            GPIO.output(LED_START, 0)
        btn_stop_prev_reading = btn_stop_reading

        # Key Switch
        btn_key_reading = GPIO.input(BTN_KEY)
        if btn_key_reading and not btn_key_prev_reading:
            print "Starting"
            threading.Thread(target=effet_boris).start()
        if not btn_key_reading and btn_key_prev_reading:
            print "Stopping"
            GPIO.output(LED_ON, 0)
        btn_key_prev_reading = btn_key_reading

        # Some sleep
        time.sleep(0.1)

finally:

    GPIO.cleanup()
