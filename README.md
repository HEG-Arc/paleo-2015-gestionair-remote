# paleo-2015-gestionair-remote
Remote control for the gestion'air service

# Remote Spec

    BTN_KEY = 23
    LED_ON = 7
    BTN_DEMO = 10
    LED_DEMO = 25
    BTN_CALL = 17
    BTN_START = 27
    LED_START = 8 
    BTN_STOP = 22


Buttton should be debounce only if value changes between reads it shoudl register an event

## BTN_KEY
    
  * ON: Should trigger led test and then get into normal operation mode
  * OFF: QUESTION: ?? lock dashboard or stop sim?

## LED_ON 
  * QUESTION: show which state? of key? (button usable)
  * OR of full simulator alls services running?

## BTN_DEMO
  * ON: Start a demo call on demo phone
  * QUESTION: Should a new button press restart demo? or do nothing unitl demo ended
    
## LED_DEMO
  While asterisk Demo channel is:
  * ringing blink
  * established Off
  * ready to do demo = ON
        
## BTN_CALL
  * PUSH: play musique
  * TODO CHECK playback if it can be interrupted/toggled
    
## BTN_START
  * PUSH: Send start to simulator
  * SET LED_START blinking until real value of state is received
    
## LED_START
  * Blinking if BTN_START
  * ON/OFF depending of real value of simulator state from sim loop
    
## BTN_STOP
  * PUSH: Send stop to simulator

# Supervisor Script

    [program:remote-control]
    command=/usr/bin/python /home/pi/paleo-2015-gestionair-remote/remote_control.py
    directory=/home/pi/paleo-2015-gestionair-remote
    autostart=true
    autorestart=true
    startretries=3
    stderr_logfile=/var/log/gestionair/remote.err.log
    stdout_logfile=/var/log/gestionair/remote.out.log
    user=root
