import math
import RPi.GPIO as GPIO
import time
from pynput import keyboard
import  CameraManager as cm
from datetime import datetime

en_arm = 5
in_values = {"arm": [6, 13], "e-magnet": [19, 26]}
pwm_pin = None

syringe_weight_full = 23
download_rate = 4.6 # this value depends on viscosity and pwm
upload_rate = None # TODO: workout this value

def setup():
    print('setting up')
    global pwm_pin
    global pwm_value
    GPIO.setup(en_arm, GPIO.OUT) 
    pwm_pin = GPIO.PWM(en_arm, 100)
    pwm_pin.start(100)
    for key, value in in_values.items():
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.output(value[0], GPIO.LOW)
        GPIO.setup(value[1], GPIO.OUT)
        GPIO.output(value[1], GPIO.LOW)
        
# This is a test fuction
def prepare_syringe():
    enable_magnet()
    global syringe_weight_full
    extend(syringe_weight_full + 5)
    retract(40, 0.5)
    disable_magnet()
    retract(100, 5)

# this is a test function
def on_press(key):
    global syringe_weight_full
    if (key == keyboard.Key.down):
        retract(100)
    elif (key == keyboard.Key.up):
        time.sleep(2)
        extend(syringe_weight_full + 5)
        retract(40)
#         extend(0)
    elif (key == keyboard.Key.left):
        print("magnet activated")
        GPIO.output(in_values['e-magnet'][0], GPIO.HIGH)
    elif key == keyboard.Key.right: 
        print("all deactivated")
        GPIO.output(in_values['arm'][0], GPIO.LOW)
        GPIO.output(in_values['arm'][1], GPIO.LOW)
        GPIO.output(in_values['e-magnet'][0], GPIO.LOW)
        GPIO.output(in_values['e-magnet'][1], GPIO.LOW)
    elif (key==keyboard.Key.space):
        for key, value in in_values.items():
            GPIO.output(value[0], GPIO.LOW)
            GPIO.output(value[1], GPIO.LOW)
    else:
        destroy()
        
def enable_magnet():
    print("magnet activated" )
    GPIO.output(in_values['e-magnet'][0], GPIO.HIGH)
    
def disable_magnet():
    print("magnet deactivated" )
    GPIO.output(in_values['e-magnet'][0], GPIO.LOW)

def extend_test(pwm):
    global old_time
    global pwm_pin
    pwm_pin.ChangeDutyCycle(pwm)
    old_time = datetime.now()
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    GPIO.output(in_values['arm'][1], GPIO.HIGH)

def extend(duration):
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    GPIO.output(in_values['arm'][1], GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
    
def extend_f(syringe_weight = None, duration = None):
    global duration_limits
    global syringe_weight_full
    duration_limits = [1.7, 4.7]
    print('extending')
    pwm_pin.ChangeDutyCycle(100)
    if syringe_weight is not None:
        duration = ((duration_limits[1] - duration_limits[0]) * syringe_weight / syringe_weight_full + duration_limits[0])
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    GPIO.output(in_values['arm'][1], GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
        
def retract(pwm, duration = 0):
    pwm_pin.ChangeDutyCycle(pwm)
    GPIO.output(in_values['arm'][0], GPIO.HIGH)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
    time.sleep(duration)
    
def load_f(target_amount):
    global download_rate
    if target_amount <= 0.1:
        pwm_pin.ChangeDutyCycle(20)
    else:
        pwm_pin.ChangeDutyCycle(30)
    GPIO.output(in_values['arm'][0], GPIO.HIGH)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
    sleep_time = target_amount / download_rate
    if sleep_time < 0.05:
        sleep_time = 0.05
    time.sleep(sleep_time)
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    
def destroy():
#     global old_time
#     print(f'time taken: {(datetime.now() - old_time).seconds}.{(datetime.now() - old_time).microseconds}')
    print("all arm deactivated")
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
    GPIO.output(in_values['e-magnet'][0], GPIO.LOW)
    GPIO.output(in_values['e-magnet'][1], GPIO.LOW)
    pwm_pin.stop()
    GPIO.cleanup() # Release all GPIO
     
         
if __name__ == '__main__':     # Program entrance
    GPIO.setmode(GPIO.BCM)
    # Collect events in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press)
    listener.start()

setup()