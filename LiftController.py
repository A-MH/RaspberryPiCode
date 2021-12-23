import math
import RPi.GPIO as GPIO
import time
from datetime import datetime

en = 13
in_values = [6, 5]
pwm_pin = None

syringe_weight_full = 23
refill_rate = 4.6 # this value depends on viscosity and pwm

def setup():
    if __name__ == "__main__":
        GPIO.setmode(GPIO.BCM)
    print('setting up LiftController')
    global pwm_pin
    GPIO.setup(en, GPIO.OUT) 
    pwm_pin = GPIO.PWM(en, 100)
    pwm_pin.start(100)
    GPIO.setup(in_values[0], GPIO.OUT)
    GPIO.output(in_values[0], GPIO.LOW)
    GPIO.setup(in_values[1], GPIO.OUT)
    GPIO.output(in_values[1], GPIO.LOW)

def extend(pwm):
    pwm_pin.ChangeDutyCycle(pwm)
    GPIO.output(in_values[1], GPIO.HIGH)
    GPIO.output(in_values[0], GPIO.LOW)

def retract(pwm):
    pwm_pin.ChangeDutyCycle(pwm)
    GPIO.output(in_values[0], GPIO.HIGH)
    GPIO.output(in_values[1], GPIO.LOW)
    
# when the actuator reaches its maximum extension or minim extension, it will automatically deactivate the arm, but we still do it manually just in case
def deactivate():
    GPIO.output(in_values[0], GPIO.HIGH)
    GPIO.output(in_values[1], GPIO.LOW)

setup()
retract(100)
    