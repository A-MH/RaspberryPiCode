#!/usr/bin/env python3
########################################################################
# Filename    : BreathingLED.py
# Description : Breathing LED
# Author      : www.freenove.com
# modification: 2019/12/27
########################################################################
import RPi.GPIO as GPIO
import time

en_front = 32    # EN front wheel
en_back = 33   # EN back wheel
en_left = 24    # EN left wheel
en_right = 26   # EN right wheel

IN11 = 29
IN12 = 31

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

    GPIO.setup(IN11, GPIO.OUT)
    GPIO.output(IN11, GPIO.LOW)

    GPIO.setup(IN12, GPIO.OUT)
    GPIO.output(IN12, GPIO.HIGH)

    p_front = GPIO.PWM(en_front, 500)      # set PWM Frequence to 500Hz
    p_front.start(100)
    p_back = GPIO.PWM(en_back, 500)      # set PWM Frequence to 500Hz
    p_back.start(100)

    p_left = GPIO.PWM(en_left, 500)      # set PWM Frequence to 500Hz
    p_left.start(0)
    p_right = GPIO.PWM(en_right, 500)      # set PWM Frequence to 500Hz
    p_right.start(0)                # set initial Duty Cycle to 0

def loop():
    while True:
        p_front.ChangeDutyCycle(0)     # set dc value as the duty cycle
        p_back.ChangeDutyCycle(0)     # set dc value as the duty cycle
        p_left.ChangeDutyCycle(100)     # set dc value as the duty cycle
        p_right.ChangeDutyCycle(100)     # set dc value as the duty cycle

def destroy():
    p_front.stop() # stop PWM
    p_back.stop() # stop PWM
    p_left.stop() # stop PWM
    p_right.stop() # stop PWM
    GPIO.cleanup() # Release all GPIO

if __name__ == '__main__':     # Program entrance
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()