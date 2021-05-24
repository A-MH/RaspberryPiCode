#!/usr/bin/env python3
########################################################################
# Filename    : BreathingLED.py
# Description : Breathing LED
# Author      : www.freenove.com
# modification: 2019/12/27
########################################################################
import RPi.GPIO as GPIO
import time
from pynput import keyboard
import LFUController as LFU

en_front = 7    # EN front wheel
en_back = 13   # EN back wheel
en_left = 21    # EN left wheel
en_right = 29   # EN right wheel

in_values = {
  "front": [8, 11],
  "back": [10, 12],
  "left": [22, 23],
  "right": [24, 26]
}

def setup():
    global p_front # front wheel
    global p_back # back wheel
    global p_left # left wheel
    global p_right # right wheel
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(en_front, GPIO.OUT)
    GPIO.setup(en_back, GPIO.OUT)
    GPIO.setup(en_left, GPIO.OUT)
    GPIO.setup(en_right, GPIO.OUT)
    
    for key, value in in_values.items():
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.output(value[0], GPIO.LOW)
        GPIO.setup(value[1], GPIO.OUT)
        GPIO.output(value[1], GPIO.LOW)

    p_front = GPIO.PWM(en_front, 500)      # set PWM Frequence to 500Hz
    p_front.start(50)
    p_back = GPIO.PWM(en_back, 500)      # set PWM Frequence to 500Hz
    p_back.start(50)
    p_left = GPIO.PWM(en_left, 500)      # set PWM Frequence to 500Hz
    p_left.start(50)
    p_right = GPIO.PWM(en_right, 500)      # set PWM Frequence to 500Hz
    p_right.start(50)                # set initial Duty Cycle to 0

def move():
    while True:
        with keyboard.Events() as events:
        # Block for as much as possible
            event = events.get(1e6)
        GPIO.output(in_values["left"][0], GPIO.LOW)
        GPIO.output(in_values["left"][1], GPIO.LOW)
        GPIO.output(in_values["right"][0], GPIO.LOW)
        GPIO.output(in_values["right"][1], GPIO.LOW)
        GPIO.output(in_values["front"][0], GPIO.LOW)
        GPIO.output(in_values["front"][1], GPIO.LOW)
        GPIO.output(in_values["back"][0], GPIO.LOW)
        GPIO.output(in_values["back"][1], GPIO.LOW)
        if (event.key == keyboard.KeyCode.from_char('w')):
            GPIO.output(in_values["left"][0], GPIO.HIGH)
            GPIO.output(in_values["right"][0], GPIO.HIGH)
        elif (event.key == keyboard.KeyCode.from_char('s')):
            GPIO.output(in_values["left"][1], GPIO.HIGH)
            GPIO.output(in_values["right"][1], GPIO.HIGH)
        elif (event.key == keyboard.KeyCode.from_char('a')):
            GPIO.output(in_values["front"][1], GPIO.HIGH)
            GPIO.output(in_values["back"][1], GPIO.HIGH)
        elif (event.key == keyboard.KeyCode.from_char('d')):
            GPIO.output(in_values["front"][0], GPIO.HIGH)
            GPIO.output(in_values["back"][0], GPIO.HIGH)

def destroy():
    p_front.stop() # stop PWM
    p_back.stop() # stop PWM
    p_left.stop() # stop PWM
    p_right.stop() # stop PWM
    GPIO.cleanup() # Release all GPIO

if __name__ == '__main__':     # Program entrance
    setup()
    try:
        move()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()