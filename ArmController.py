import math
import RobotSpecific as rs
import RPi.GPIO as GPIO
import time
from pynput import keyboard
from datetime import datetime
import asyncio
import busio
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


en_arm = 10
in_values = {"arm": [9, 11], "e-magnet": [19, 26]}
pwm_pin = None
zero_mark_actuator = 0 # value of potentiometer when syringe is empty
zero_mark_syringe = 7700 # value of potentiometer when syringe is empty
full_mark = 25000 # value of potentiometer when syringe is full
syringe_weight_full = 20.8

def setup():
    # Create the I2C bus for potentiometer
    global i2c
    i2c = I2C(3)
    # Create the ADC object using the I2C bus
    global ads
    ads = ADS.ADS1015(i2c, data_rate = 3300)
    # Create single-ended input on channel 
    global potentiometer
    potentiometer = AnalogIn(ads, ADS.P2)
    
    print('setting up ArmController')
    if __name__ == '__main__':
        GPIO.setmode(GPIO.BCM)
    global pwm_pin
    global en_arm
    global in_values
    GPIO.setup(en_arm, GPIO.OUT) 
    pwm_pin = GPIO.PWM(en_arm, 500)
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
    if (key == keyboard.Key.down):
        print("moving down")
        asyncio.run(retract(target_mark = zero_mark_actuator, pwm=100))
        print("finished moving down")
    elif (key == keyboard.Key.up):
        # to test positioning accuracy of the actuator. test with syringe_weight = 0 and 20.8 (which is a volume of 20)
        asyncio.run(extend_test())
        print("finished moving up")
    elif (key == keyboard.Key.left):
        print("magnet activated")
        GPIO.output(in_values['e-magnet'][1], GPIO.HIGH)
    elif key == keyboard.Key.right: 
        print("all deactivated")
        GPIO.output(in_values['arm'][0], GPIO.LOW)
        GPIO.output(in_values['arm'][1], GPIO.LOW)
        GPIO.output(in_values['e-magnet'][1], GPIO.LOW)
    elif (key==keyboard.Key.space):
        for key, value in in_values.items():
            GPIO.output(value[0], GPIO.LOW)
            GPIO.output(value[1], GPIO.LOW)
    else:
        destroy()
        
async def extend_test():
    pwm_pin.ChangeDutyCycle(100)
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    GPIO.output(in_values['arm'][1], GPIO.HIGH)
    await asyncio.sleep(10)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
    print(convert_mark2weight(potentiometer.value))


def enable_magnet():
    print("magnet activated" )
    GPIO.output(in_values['e-magnet'][1], GPIO.HIGH)
    
def disable_magnet():
    print("magnet deactivated" )
    GPIO.output(in_values['e-magnet'][1], GPIO.LOW)

def convert_weight2mark(weight):
    return zero_mark_syringe + (weight / syringe_weight_full) * (full_mark - zero_mark_syringe)

def convert_mark2weight(mark):
    return (mark - zero_mark_syringe) / (full_mark - zero_mark_syringe) * syringe_weight_full

async def extend(weight = None, homing_pwm = 25):
#     print(f"extending arm. weight: {weight}, homing_pwm: {homing_pwm}")
    target_mark = convert_weight2mark(weight)
    pwm_pin.ChangeDutyCycle(100)
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    GPIO.output(in_values['arm'][1], GPIO.HIGH)
    # while distance left is more than 2000 marks, the go at full speed
    while potentiometer.value + 2000 < target_mark:
        await asyncio.sleep(0)
    # when distance left is less than 2000 marks slow down
    pwm_pin.ChangeDutyCycle(homing_pwm)
    while potentiometer.value < target_mark:
        await asyncio.sleep(0)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
    # The following wait is there to make sure arm has fully stopped before reading potentiometer value
    await asyncio.sleep(0.2)
    return convert_mark2weight(potentiometer.value)

async def extend_refill(conc_weight_available):
    wasted_push = 0.2
    if conc_weight_available < syringe_weight_full:
        return await extend(conc_weight_available, homing_pwm = 50) - wasted_push
    else:
        return await extend(syringe_weight_full, homing_pwm = 50) - wasted_push
    
async def retract(target_mark = zero_mark_actuator, pwm = 100, homing_pwm = 20):
    pwm_pin.ChangeDutyCycle(pwm)
    GPIO.output(in_values['arm'][0], GPIO.HIGH)
    GPIO.output(in_values['arm'][1], GPIO.LOW)
    # while distance left is more than 2000 marks, the go at full speed
    while potentiometer.value > target_mark + 2000:
        await asyncio.sleep(0)
    # when distance left is less than 2000 marks slow down
    pwm_pin.ChangeDutyCycle(homing_pwm)
    while potentiometer.value > target_mark:
        await asyncio.sleep(0)
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    # The following wait is there to make sure arm has fully stopped before reading potentiometer value
    await asyncio.sleep(0.2)
    return convert_mark2weight(potentiometer.value)
    
async def retract_fill(target_amount):
#     print(f"retract filling, target_amount: {target_amount}")
    if target_amount == 0:
        return;
    marks_per_gram = 890
    mark_distance = target_amount * marks_per_gram
    target_mark = potentiometer.value - mark_distance
    wasted_pull = 0.2
    return await retract(target_mark, pwm = 100) + wasted_pull
    
def stop_arm():
    GPIO.output(in_values['arm'][0], GPIO.LOW)
    GPIO.output(in_values['arm'][1], GPIO.LOW)

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
     
# CAUTION: THIS SHOULD COME BEFORE NAME == MAIN
setup()

if __name__ == '__main__':     # Program entrance
    # Collect events in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press)
    listener.start()
