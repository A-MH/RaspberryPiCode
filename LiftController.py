import math
import RPi.GPIO as GPIO
import time
from datetime import datetime

en = 13
in_values = [6, 5]
pwm_pin = None

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

def extend_test():
    GPIO.output(in_values[1], GPIO.HIGH)
    GPIO.output(in_values[0], GPIO.LOW)
    return sleep_time

def extend_phase1(conc_weight):
    conc_weight_full = 90
    gram_per_second = 25
    pre_engagement_duration = 1.8
    sleep_time = pre_engagement_duration + (conc_weight_full - conc_weight) / gram_per_second
    pwm_pin.ChangeDutyCycle(100)
    GPIO.output(in_values[1], GPIO.HIGH)
    GPIO.output(in_values[0], GPIO.LOW)
    return sleep_time
    
def extend_phase2(refill_pwm):
    ratio = 0.37
    pwm = refill_pwm * ratio
    pwm_pin.ChangeDutyCycle(pwm)
    GPIO.output(in_values[1], GPIO.HIGH)
    GPIO.output(in_values[0], GPIO.LOW)

def retract(pwm = 100):
    pwm_pin.ChangeDutyCycle(pwm)
    GPIO.output(in_values[0], GPIO.HIGH)
    GPIO.output(in_values[1], GPIO.LOW)
    
def stop_lift():
    pwm_pin.ChangeDutyCycle(0)
    GPIO.output(in_values[0], GPIO.LOW)
    GPIO.output(in_values[1], GPIO.LOW)
    
# when the actuator reaches its maximum extension or minim extension, it will automatically deactivate the arm,
#but we still do it manually just in case
def deactivate():
    GPIO.output(in_values[0], GPIO.HIGH)
    GPIO.output(in_values[1], GPIO.LOW)

setup()

if __name__ == "__main__":
    retract()
#     extend_test()
#     time.sleep(extend_phase1(67.4))
#     stop_lift()
    
# extend(100)
    