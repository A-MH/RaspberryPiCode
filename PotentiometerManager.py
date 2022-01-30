import math
import RPi.GPIO as GPIO
import time

signal = 22


en_arm = 10
in_values = {"arm": [9, 11], "e-magnet": [19, 26]}

def setup():
    print('setting up potentiometer')
    if __name__ == '__main__':
        GPIO.setmode(GPIO.BCM)
    global pwm_pin
    pwm_pin = GPIO.PWM(en_arm, 100)
    pwm_pin.start(100)
    for key, value in in_values.items():
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.setup(value[1], GPIO.OUT)
        # if it is the magnet pin, it is using the simple mosfet and its values need be send differently
        if key == "e-magnet":
            GPIO.output(value[0], GPIO.HIGH) # this is vcc and should be high
            GPIO.output(value[1], GPIO.LOW)
        else:
            GPIO.output(value[0], GPIO.LOW)
            GPIO.output(value[1], GPIO.LOW)