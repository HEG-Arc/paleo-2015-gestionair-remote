import threading
import RPi.GPIO as GPIO
import time
import requests
import json
import logging
import memcache


BTN_KEY = 23
BTN_DEMO = 10
BTN_CALL = 17
BTN_START = 27
BTN_STOP = 22
LED_ON = 7
LED_DEMO = 25
LED_START = 8 


URL_DEMO = "/scheduler/demo/"
URL_CALL = "/scheduler/call/"
URL_START = "/scheduler/start/"
URL_STOP = "/scheduler/stop/"
URL_STATUS = "/scheduler/status/"


COMMAND_URL = {'DEMO': URL_DEMO, 'CALL': URL_CALL, 'START': URL_START, 'STOP': URL_STOP, 'STATUS': URL_STATUS}


LOGIN = "http://192.168.1.127:8000/accounts/login/"
USERNAME = 'paleo'
PASSWORD = 'paleo'


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


logger = logging.getLogger("Gestion'air Remote")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/gestionair/remote.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Starting the Gestion'air Remote daemon...")

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

client = requests.session()

check_status_stop = threading.Event()

def get_url(url):
    # Retrieve the CSRF token first
    client.get(LOGIN)  # sets the cookie
    csrftoken = client.cookies['csrftoken']
    data = dict(login=USERNAME, password=PASSWORD, csrfmiddlewaretoken=csrftoken, next=url)
    r = client.post(LOGIN, data=data, headers={"Referer": "http://192.168.1.127:8000/"})
    print r.content
    return json.loads(r.content)


def process_command(command):
    if command in COMMAND_URL:
        logger.info("Process command: %s" % command)
        confirmation = get_url(COMMAND_URL[command])
        if confirmation['success']:
            logger.info("Command %s sucessfully sent: %s" % (command, confirmation['message']))
            if command == "STOP":
                GPIO.output(LED_START, 0)
            elif command == "START":
                GPIO.output(LED_START, 1)
            elif command == "DEMO":
                threading.Thread(target=blink, args=(LED_DEMO, 6, True)).start()
        else:
            logger.info("Command %s failed: %s" % (command, confirmation['message']))
    else:
        logger.info("Wrong command: %s" % command)


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


def check_status(check_status_stop):
    # TODO: Add a way to restart if unable to get the URL
    game_status = False
    demo_status = False
    while(not check_status_stop.is_set()):
        status = get_url(URL_STATUS)
        if status['game'] != game_status:
            if game_status == "RUNNING":
                # The game finished
                GPIO.output(LED_START, 0)
            game_status = status['game']
        if status['demo'] != demo_status:
            if demo_status == "RUNNING":
                # The game finished
                GPIO.output(LED_DEMO, 0)
            demo_status = status['demo']
        check_status_stop.wait(1)
        pass


threading.Thread(target=check_status, args=(check_status_stop,)).start()


try:
    while True:
        # Button DEMO
        btn_demo_reading = GPIO.input(BTN_DEMO)
        if btn_demo_reading and not btn_demo_prev_reading:
            print "Demo"
            threading.Thread(target=process_command, args=('DEMO',)).start()
        btn_demo_prev_reading = btn_demo_reading

        # Button CALL
        btn_call_reading = GPIO.input(BTN_CALL)
        if btn_call_reading and not btn_call_prev_reading:
            print "Call"
            threading.Thread(target=process_command, args=('CALL',)).start()
        btn_call_prev_reading = btn_call_reading

        # Button START
        btn_start_reading = GPIO.input(BTN_START)
        if btn_start_reading and not btn_start_prev_reading:
            print "Start"
            threading.Thread(target=process_command, args=('START',)).start()
        btn_start_prev_reading = btn_start_reading

        # Button STOP
        btn_stop_reading = GPIO.input(BTN_STOP)
        if btn_stop_reading and not btn_stop_prev_reading:
            print "Stop"
            threading.Thread(target=process_command, args=('STOP',)).start()
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
    logger.info("Terminating the Gestion'air Remote daemon...")
    check_status_stop.set()
    GPIO.cleanup()
