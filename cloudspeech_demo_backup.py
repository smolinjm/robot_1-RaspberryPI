#!/usr/bin/env python3

# python3 ~/AIY-projects-python/src/examples/voice/cloudspeech_demo_backup.py

import os
import contextlib
#import playsound
#from playsound import playsound
#import audioplayer as ap
import random

with contextlib.redirect_stdout(None):
    #import pygame
    from pygame import mixer

import argparse
import locale
import logging
import datetime
import time
from time import sleep
from gpiozero import LED

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient

import RPi.GPIO as GPIO
import time

from gtts import gTTS
from pathlib import Path

import asyncio
from threading import Thread
#from multiprocessing import Process

    

async def get_GTTS(say,my_path):
    output = gTTS(text=say,lang='en', slow=False)
    output.save(my_path)
    return output

async def get_mixer_file(mixer,my_path_abs):
    mixer.music.load(my_path_abs)
    return mixer

async def playSound(say):
    print('sound. ',say)
    my_file = say.replace(' ','_')
    my_path = Path(str(os.getcwd())+"/robot_voice/"+my_file+'.mp3')
    my_path_abs = 'robot_voice/'+my_file+'.mp3'
    try:
        my_abs_path = my_path.resolve(strict=True)
    except FileNotFoundError:
        # doesn't exist
        #if mixer.get_init() == True:
            #mixer.quit()
        output = await get_GTTS(say,my_path)
        #output = gTTS(text=say,lang='en', slow=False)
        #output.save(my_path)
        #mixer.init()
        #mixer = await get_mixer_file(mixer,my_path_abs)
        #mixer.music.load(my_path_abs)
        #mixer.music.play()
        await playSound(say)
        #ap.AudioPlayer(my_path).play(block=True)
    else:
        # exists
        #playsound(my_path)
        #if mixer.get_init() == True:
            #mixer.quit()
        await init_mixer(my_path_abs)
        #p.AudioPlayer(my_path).play(block=True)
        
    if "suffering" in say: 
        await asyncio.sleep(2)
    await asyncio.sleep(2)
    return
    


async def init_mixer(path):
    mixer.init()
    mixer.music.load(path)
    mixer.music.play()





def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('light on',
                'light off',
                'blink light',
                'end program / quit',
                'left',
                'right',
                'stop blinking')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

async def blink_led(led,num):
    for i in range(0,num):
        led.on()
        await asyncio.sleep(.1)
        led.off()
        await asyncio.sleep(.1)
    return
        
async def servo_wave(p):
    k = random.randint(2, 4)
    x = random.randint(1, 3)
    xx = x/10
    print(f'{k}, {x}, {xx}')
    #p.start(CENTRE)
    for i in range(k):
        p.ChangeDutyCycle(MIN_DUTY)
        await asyncio.sleep(xx)
        p.ChangeDutyCycle(CENTRE)
        await asyncio.sleep(xx)
        p.ChangeDutyCycle(MAX_DUTY)
        await asyncio.sleep(xx)
        p.ChangeDutyCycle(CENTRE)
        await asyncio.sleep(xx)
    #p.stop()
    return

async def servo_move_right(p):
    p.ChangeDutyCycle(MIN_DUTY)
    await asyncio.sleep(0.3)
    p.ChangeDutyCycle(CENTRE)
    return
    
async def servo_move_left(p):
    p.ChangeDutyCycle(MAX_DUTY)
    await asyncio.sleep(0.3)
    p.ChangeDutyCycle(CENTRE)
    return


async def sayTime():
    
    now = datetime.datetime.now()
    h = now.hour
    if now.hour > 12:
        h = now.hour - 12
    m = str(now.minute)
    if now.minute < 10:
        m = "o "+str(now.minute)
    if now.minute == 0:
        m = "o clock"
    
    text = 'Its '+str(h)+', '+m
    print('time. ',text)
    await playSound(text)
    await asyncio.sleep(1)
    return

MIN_DUTY = 3
MAX_DUTY = 11
CENTRE = MIN_DUTY + (MAX_DUTY - MIN_DUTY) / 2

'''
async def motion_detection_loop(pirpin,led):
    try:
        GPIO.add_event_detect(pirpin,GPIO.RISING,callback=motionLight_on)
        while 1:
            if GPIO.input(pirpin):
                print('motion...')
                led.on()
                sleep(1)
            else:
                led.off()
                sleep(1)
                
    except KeyboardInterrupt:
        print('motion cleanup.')
        GPIO.cleanup()
'''     
#global current_motionEvent
#current_motionEvent = False

global led
led = LED(26)

def motionLight_on():
    print('...motion dectected...')
    global led
    led.on()
    time.sleep(2)
    led.off()
    #GPIO.remove_event_detect(24)
    #global current_motionEvent
    #current_motionEvent = False
    return

def createMotionEvent(pirpin):
    global current_motionEvent
    print('activate motion check. ',current_motionEvent)
    if current_motionEvent != True:
        GPIO.add_event_detect(pirpin,edge=GPIO.BOTH,callback=motionLight_on,bouncetime=1000)
        current_motionEvent = True
    return

async def keep_eye_open():
    pirpin = 24
    
    GPIO.setup(pirpin,GPIO.IN)
    global led
    
    time.sleep(.1)
    
    while True:
        
        #print(GPIO.input(pirpin),' PIN -',pirpin)
        if GPIO.input(pirpin):
            motionLight_on()
            await playSound('motion detected')
            await asyncio.sleep(30)
        else:
            led.off()
        time.sleep(2)
        
    '''
    try:
        time.sleep(2)
        
    except KeyboardInterrupt:
        print('quit')
        led.off()
        GPIO.cleanup()
    '''    
    return


async def listen_up():
    #os.system('start output.mp3')

    MIN_DUTY = 3
    MAX_DUTY = 11
    CENTRE = MIN_DUTY + (MAX_DUTY - MIN_DUTY) / 2

    servo_pin = 5
    duty_cycle = CENTRE     # Should be the centre for a SG90

    # Configure the Pi to use pin names (i.e. BCM) and allocate I/O
    
    GPIO.setup(servo_pin, GPIO.OUT)

    # Create PWM channel on the servo pin with a frequency of 50Hz
    pwm_servo = GPIO.PWM(servo_pin, 50)
    pwm_servo.start(duty_cycle)

    #CENTRE = MIN_DUTY + (MAX_DUTY - MIN_DUTY) / 2
    pwm_servo.start(CENTRE)
    
    
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    
    global led
    #import sys
    #sys.exit()
    
    pwm_servo.ChangeDutyCycle(CENTRE)
    
    #await motion_detection_loop(pirpin,led)
    #GPIO.add_event_detect(pirpin,GPIO.RISING,callback=motionLight_on) 
    #createMotionEvent(pirpin)
    
    #GPIO.add_event_detect(pirpin,edge=GPIO.RISING,callback=motionLight_on,bouncetime=100)
    
    #print('HERE.')
    with Board() as board:
        try:
            while True:
                
                if hints:
                    logging.info('Say something, e.g. %s.' % ', '.join(hints))
                else:
                    logging.info('Say something.')
                print('pretext. ',args.language)
                text = client.recognize(language_code=args.language,
                                        hint_phrases=hints)
                #print('text.')
                if text is None:
                    #print('FUCKING. STOP.')
                    #time.sleep(100000)
                    os.system('clear')
                    #createMotionEvent(pirpin)
                    logging.info('You said nothing.')
                    now = datetime.datetime.now()
                    if now.minute == 0:
                        if now.hour > 7 and now.hour < 21:
                            sayTime()
                            time.sleep(60)
                    continue
                
                
                
                logging.info('You said: "%s"' % text)
                text = text.lower()
                
                
                if 'light on' in text :
                    #aiy.audio.say('let there be light')
                    #gpio.output(26,gpio.HIGH)
                    led.on()
                    board.led.state = Led.ON
                    await asyncio.gather(playSound('the light should be on now'))
                elif 'light off' in text :
                    #aiy.audio.say('I cast you into darkness')
                    #gpio.output(26,gpio.LOW)
                    led.off()
                    board.led.state = Led.OFF
                    await asyncio.gather(playSound("the light should be off"))
                    
                elif 'stop blinking' in text :
                    board.led.state = Led.OFF
                    await asyncio.gather(playSound('blinking stopped'))
                elif 'blink light' in text or 'light blink' in text or 'blink' in text :
                    #aiy.audio.say('blink')
                    board.led.state = Led.BLINK
                    await asyncio.gather(playSound('the light should be blinking'),blink_led(led,5))
                elif 'move arm right' in text or 'right' in text :
                    await asyncio.gather( blink_led(led,3), servo_move_right(pwm_servo), playSound('moved right') )
                elif 'move arm left' in text or 'left' in text :
                    await asyncio.gather( blink_led(led,2), servo_move_left(pwm_servo), playSound('moved left') )
                elif 'good job robot' in text :
                    x = random.choice([
                        "good job to you too",
                        "we make a great team",
                        "thanks",
                        "your appreciation has been noted"
                        ])
                    await asyncio.gather(playSound(x))
                elif 'say something silly' in text :
                    #playSound("don't tell me what to do")
                    await asyncio.gather(playSound("don't tell me what to do"))
                elif 'testing 1 2 3' in text :
                    await playSound("testing Testing TESTING")
                elif 'say something stupid' in text :
                    #playSound('uhhhh ummmm ... duhhhhh')
                    await asyncio.gather(playSound('uhhhh ummmm ... duhhhhh'))
                elif 'say' in text :
                    x = text[int(text.index('say')+4):]
                    #x = text.replace('say ','')
                    #playSound(x)
                    await asyncio.gather(playSound(x))
                elif 'arm stop' in text or 'stop arm' in text or 'stop' in text:
                    GPIO.cleanup()
                    board.led.state = Led.OFF
                    #playSound('arm stop')
                    await asyncio.gather(playSound('arm stop'))
                elif 'goodbye' in text or 'end program' in text or 'quit' in text or 'exit' in text:
                    #aiy.audio.say('goodbye')
                    GPIO.cleanup()
                    #playSound('goodbye')
                    await asyncio.gather(playSound('goodbye'))
                    await asyncio.sleep(3)
                    break
                elif 'robot' in text :
                    x = random.choice([
                        "what",
                        "what can I do for you master?",
                        "yes?",
                        "robot, at your service",
                        "hey"
                        ])
                    #playSound(x)
                    await asyncio.gather(playSound(x))
                elif 'time it is' in text :
                    x = random.choice([
                        "I do",
                        "yes",
                        "knowing the time is escential to my being."
                        ])
                    await playSound(x)
                elif 'time is it' in text :
                    await sayTime()
                elif 'hello' in text :
                    x = random.choice(["hi there",
                        "hi",
                        "hey",
                        "what up",
                        "yo",
                        "hello",
                        "yow"
                        ])
                    await asyncio.gather( playSound(x),blink_led(led,5),servo_wave(pwm_servo), )
                elif 'wave' in text :
                    await asyncio.gather( blink_led(led,5),servo_wave(pwm_servo) )
                else:
                    x = random.choice([
                        "I don't understand",
                        "I didn't catch that",
                        "what?",
                        "wut",
                        "wat",
                        "I beg your pardon?",
                        "Can you please repeat that?",
                        "please try again",
                        "one more time please",
                        "you're not talking to me are you."
                        ])
                    await asyncio.gather(playSound(x))
                
                
        except KeyboardInterrupt:
            GPIO.cleanup()
            
    return
    


'''
async def main():
    
    while True:
        await keep_eye_open()
        await listen_up()

    return
'''            


def test1():
    print('keep_eye_open')
    #asyncio.run(keep_eye_open())
    loop1 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop1)
    #loop1.call_soon(keep_eye_open,loop1)
    asyncio.ensure_future(keep_eye_open())
    loop1.run_forever()
    return

def test2():
    print('listen_up')
    #asyncio.run(listen_up())
    loop2 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop2)
    #loop2.call_soon(listen_up,loop2)
    asyncio.ensure_future(listen_up())
    loop2.run_forever()
    return
                

if __name__ == '__main__':
    #asyncio.run(main())
    GPIO.setmode(GPIO.BCM)
    
    #t1 = Thread(target=test2()).start()
    #t2 = Thread(target=test1()).start()
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(keep_eye_open())
        asyncio.ensure_future(listen_up())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
    
    #t1 = Process(target=test1())
    #t1.start()
    #t2 = Process(target=test2())
    #t2.start()
    
    #t1.daemon = False
    #t2.daemon = False
    #t1.start()
    #t2.start()
    
    
    #Thread(target=keep_eye_open).start()
    #Thread(target=listen_up).start()
    
    '''
    loop = asyncio.get_event_loop()
    eye_future = loop.create_task(keep_eye_open())
    ear_future = loop.create_task(listen_up())
    
    try:
        loop.run_forever()
    except keyboardInterrupt:
        loop.stop()
        loop.close()
    '''



'''
try:
    while True:
        pwm_servo.ChangeDutyCycle(MIN_DUTY)
        time.sleep(0.5)
        pwm_servo.ChangeDutyCycle(CENTRE)
        time.sleep(0.5)
        pwm_servo.ChangeDutyCycle(MAX_DUTY)
        time.sleep(0.5)
        pwm_servo.ChangeDutyCycle(CENTRE)
        time.sleep(0.5)
            
except KeyboardInterrupt:
    print("CTRL-C: Terminating program.")
finally:
    print("Cleaning up GPIO...")
    pwm_servo.ChangeDutyCycle(CENTRE)
    time.sleep(0.5)
    GPIO.cleanup()
    
import sys
sys.exit()
'''
