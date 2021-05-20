#!/usr/bin/env python3
########################################################################
# Filename    : BreathingLED.py
# Description : Breathing LED
# Author      : www.freenove.com
# modification: 2019/12/27
########################################################################
import RPi.GPIO as GPIO
import time

EN11 = 32    # motor controller 1
EN12 = 33   # motor controller 2
EN21 = 24    # motor controller 1
EN22 = 26   # motor controller 2

IN11 = 29
IN12 = 31

def setup():

    global p11
    global p12
    global p21
    global p22
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(EN11, GPIO.OUT)
    GPIO.setup(EN12, GPIO.OUT)
    GPIO.setup(EN21, GPIO.OUT)
    GPIO.setup(EN22, GPIO.OUT)

    GPIO.setup(IN11, GPIO.OUT)
    GPIO.output(IN11, GPIO.LOW)

    GPIO.setup(IN12, GPIO.OUT)
    GPIO.output(IN12, GPIO.HIGH)

    p11 = GPIO.PWM(EN11, 500)      # set PWM Frequence to 500Hz
    p11.start(100)
    p12 = GPIO.PWM(EN12, 500)      # set PWM Frequence to 500Hz
    p12.start(100)

    p21 = GPIO.PWM(EN21, 500)      # set PWM Frequence to 500Hz
    p21.start(0)
    p22 = GPIO.PWM(EN22, 500)      # set PWM Frequence to 500Hz
    p22.start(0)                # set initial Duty Cycle to 0

def loop():
    while True:
        p11.ChangeDutyCycle(100)     # set dc value as the duty cycle
        p12.ChangeDutyCycle(100)     # set dc value as the duty cycle
        p21.ChangeDutyCycle(0)     # set dc value as the duty cycle
        p22.ChangeDutyCycle(0)     # set dc value as the duty cycle

def destroy():
    p11.stop() # stop PWM
    p12.stop() # stop PWM
    p21.stop() # stop PWM
    p22.stop() # stop PWM
    GPIO.cleanup() # Release all GPIO

if __name__ == '__main__':     # Program entrance
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()