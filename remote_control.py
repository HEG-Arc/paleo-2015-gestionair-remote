import threading
import RPi.GPIO as GPIO
#from GPIOEmulator.EmulatorGUI import GPIO
import time
import requests
import json
import logging

API_URL = 'http://192.168.1.1'


class Led(object):
    def __init__(self, gpio):
        self.gpio = gpio
        self._stop = None
        self.blinking = False

    def blink(self):
        if self.blinking:
            return
        self.blinking = True
        self._stop = threading.Event()
        threading.Thread(target=self._blink).start()

    def _blink(self):
        out = True
        while not self._stop.is_set():
            GPIO.output(self.gpio, int(out))
            out = not out
            self._stop.wait(0.3)

    def _blink_stop(self):
        self.blinking = False
        if self._stop:
            self._stop.set()

    def set(self, on):
        if on: self.on()
        else: self.off()

    def on(self):
        self._blink_stop()
        GPIO.output(self.gpio, 1)

    def off(self):
        self._blink_stop()
        GPIO.output(self.gpio, 0)

BTN_KEY = 23
LED_ON_GPIO = 7
LED_ON = Led(LED_ON_GPIO)
BTN_DEMO = 10
LED_DEMO_GPIO = 25
LED_DEMO = Led(LED_DEMO_GPIO)
BTN_CALL = 17
BTN_START = 27
LED_START_GPIO = 8
LED_START = Led(LED_START_GPIO)
BTN_STOP = 22

# setup GPIO for remote
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_KEY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_DEMO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_CALL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_START, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_STOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_ON_GPIO, GPIO.OUT)
GPIO.setup(LED_DEMO_GPIO, GPIO.OUT)
GPIO.setup(LED_START_GPIO, GPIO.OUT)

GPIO.output(LED_ON_GPIO, 0)
GPIO.output(LED_DEMO_GPIO, 0)
GPIO.output(LED_START_GPIO, 0)

logger = logging.getLogger("Gestion'air Remote")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("remote.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Starting the Gestion'air Remote daemon...")


def effect_start():
    for i in range(1,6):
        GPIO.output(LED_START_GPIO, 0)
        GPIO.output(LED_ON_GPIO, 1)
        time.sleep(0.2)
        GPIO.output(LED_ON_GPIO, 0)
        GPIO.output(LED_DEMO_GPIO, 1)
        time.sleep(0.2)
        GPIO.output(LED_DEMO_GPIO, 0)
        GPIO.output(LED_START_GPIO, 1)
        time.sleep(0.2)
    GPIO.output(LED_START_GPIO, 0)
    GPIO.output(LED_ON_GPIO, 1)


def key_event(channel):
    # ON: Should trigger led test and then get into normal operation mode
    if GPIO.input(BTN_KEY) == 0:
        effect_start()
        LED_ON.on()
    else:
        # OFF: QUESTION: ?? lock dashboard or stop sim?
        LED_ON.off()
        LED_DEMO.off()

GPIO.add_event_detect(BTN_KEY, GPIO.BOTH, callback=key_event)


def start_event(channel):
    requests.get(API_URL + '/game/start')
    LED_START.blink()

GPIO.add_event_detect(BTN_START, GPIO.FALLING, callback=start_event, bouncetime=500)


def stop_event(channel):
    requests.get(API_URL + '/game/stop')
    LED_START.blink()

GPIO.add_event_detect(BTN_STOP, GPIO.FALLING, callback=stop_event, bouncetime=500)


def call_event(channel):
    requests.get(API_URL + '/game/api/play-sound/call')

GPIO.add_event_detect(BTN_CALL, GPIO.FALLING, callback=call_event, bouncetime=500)


def demo_event(channel):
    requests.get(API_URL + '/game/api/call/1201')
    LED_DEMO.blink()

GPIO.add_event_detect(BTN_DEMO, GPIO.FALLING, callback=demo_event, bouncetime=500)


try:
    while True:
        if GPIO.input(BTN_KEY) == 0:
            # check sim status for leds
            try:
                res = requests.get(API_URL + '/game/api/status').json()
                LED_ON.on()
            except:
                res = {
                    'isRunning': False,
                    'demoState': 'ERROR',
                }
                LED_ON.blink()
            ## led_on ??
            LED_START.set(res['isRunning'])

            # on indicate ready for demo, blinking during ringing, off during answer
            if res['demoState'] == 'FREE':
                LED_DEMO.on()
            elif res['demoState'] == 'RINGING':
                LED_DEMO.blink()
            else:
                LED_DEMO.off()

        # some sleep
        time.sleep(1)

finally:
    logger.info("Terminating the Gestion'air Remote daemon...")
    GPIO.cleanup()
