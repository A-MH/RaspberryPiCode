#!/usr/bin/env python3
########################################################################
# Filename    : BreathingLED.py
# Description : Breathing LED
# Author      : www.freenove.com
# modification: 2019/12/27
########################################################################
import math
import RPi.GPIO as GPIO
import time
from pynput import keyboard
# import LFUController as LFU
import asyncio
from simple_pid import PID
import matplotlib.pyplot as plt

pwm_value = 100

wd = 21.5 # wheel distance (distance between two opposite wheels

en_arm = 22
in_values = {"arm": [23, 24], "e-magnet": [6, 10]}
pwm_pin = None


def on_press(key):
    if (key == keyboard.Key.down):
        GPIO.output(in_values['arm'][0], GPIO.HIGH)
        GPIO.output(in_values['arm'][1], GPIO.LOW)
    elif (key == keyboard.Key.up):
        GPIO.output(in_values['arm'][0], GPIO.LOW)
        GPIO.output(in_values['arm'][1], GPIO.HIGH)
    elif (key == keyboard.Key.left):
        print("2")
        GPIO.output(in_values['e-magnet'][0], GPIO.HIGH)
        GPIO.output(in_values['e-magnet'][1], GPIO.LOW)
    else:
        GPIO.output(in_values['arm'][0], GPIO.LOW)
        GPIO.output(in_values['arm'][1], GPIO.LOW)
        GPIO.output(in_values['e-magnet'][0], GPIO.LOW)
        GPIO.output(in_values['e-magnet'][1], GPIO.LOW)
        destroy()

def destroy():
    pwm_pin.stop()
    GPIO.cleanup() # Release all GPIO
    
# Collect events in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press)
listener.start()

def setup():
    global pwm_pin
    global pwm_value
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(en_arm, GPIO.OUT) 
    pwm_pin = GPIO.PWM(en_arm, 100)
    pwm_pin.start(pwm_value)
    for key, value in in_values.items():
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.output(value[0], GPIO.LOW)
        GPIO.setup(value[1], GPIO.OUT)
        GPIO.output(value[1], GPIO.LOW)
        
if __name__ == '__main__':     # Program entrance
    setup()