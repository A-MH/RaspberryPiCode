#!/usr/bin/env python3
########################################################################
# Filename    : BreathingLED.py
# Description : Breathing LED
# Author      : www.freenove.com
# modification: 2019/12/27
########################################################################
import math
import RPi.GPIO as GPIO
from datetime import datetime
from pynput  import keyboard
import LFUController as LFU
import asyncio
from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np

sample_time = 0.005

is_accelerating = True
is_decelerating = False

pwm = 0

wd = 21.5 # wheel distance (distance between two opposite wheels
    
default_pwm = 20
pwm_acceleration = 1000 * default_pwm
pwm_deceleration = 2 * default_pwm

en_values = {"right": 20, "left": 8, "front": 25, "back": 17}

pwm_pins = {"front": None, "back": None, "left": None, "right": None}
     
in_values = {"right": [12, 16], "left": [1, 7], "front": [24, 23], "back": [15, 18]}
     
pwm_multipliers = {"front": 1, "back": 1, "left": 1, "right": 1}

end_offsets = [-4, -2, -4, -2]

deviations = np.zeros([0,4])

travel_distance = 3

ctrl_held = False

def on_press(key):
    global travel_direction
    global ctrl_held
    global end_offsets
    if (key == keyboard.Key.up):
        go_to_dest("front")
    elif(key == keyboard.Key.down):
        go_to_dest("back")
    elif(key == keyboard.Key.left):
        go_to_dest("left")
    elif(key == keyboard.Key.right):
        go_to_dest("right")
    elif key == keyboard.Key.ctrl:
        ctrl_held = True
    elif(key == keyboard.Key.space):
        GPIO.output(in_values["left"][0], GPIO.LOW)
        GPIO.output(in_values["left"][1], GPIO.LOW)
        GPIO.output(in_values["right"][0], GPIO.LOW)
        GPIO.output(in_values["right"][1], GPIO.LOW)
        GPIO.output(in_values["front"][0], GPIO.LOW)
        GPIO.output(in_values["front"][1], GPIO.LOW)
        GPIO.output(in_values["back"][0], GPIO.LOW)
        GPIO.output(in_values["back"][1], GPIO.LOW)
    elif key.char == "c" and ctrl_held:
        destroy() 

def on_release(key):
    global ctrl
    if key == keyboard.Key.ctrl:
        ctrl_held = False

def setup():
    GPIO.setmode(GPIO.BCM)
    global pwm_pins
    global pwm_values
    for key, value in in_values.items():
        GPIO.setup(en_values[key], GPIO.OUT) 
        pwm_pins[key] = GPIO.PWM(en_values[key], 500) 
        pwm_pins[key].start(default_pwm * pwm_multipliers[key])
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.output(value[0], GPIO.LOW)
        GPIO.setup(value[1], GPIO.OUT)
        GPIO.output(value[1], GPIO.LOW)

def go_to_dest(direction):
    print(f"start time {datetime.now().strftime('%S.%f')[:-4]}")
    GPIO.output(in_values["left"][0], GPIO.LOW)
    GPIO.output(in_values["left"][1], GPIO.LOW)
    GPIO.output(in_values["right"][0], GPIO.LOW)
    GPIO.output(in_values["right"][1], GPIO.LOW)
    GPIO.output(in_values["front"][0], GPIO.LOW)
    GPIO.output(in_values["front"][1], GPIO.LOW)
    GPIO.output(in_values["back"][0], GPIO.LOW)
    GPIO.output(in_values["back"][1], GPIO.LOW)
    if direction == "front":
        GPIO.output(in_values["left"][0], GPIO.HIGH)
        GPIO.output(in_values["right"][1], GPIO.HIGH)
    elif direction == "back":
        GPIO.output(in_values["left"][1], GPIO.HIGH)
        GPIO.output(in_values["right"][0], GPIO.HIGH)
    elif direction == "left":
        GPIO.output(in_values["front"][0], GPIO.HIGH)
        GPIO.output(in_values["back"][1], GPIO.HIGH)
    else:
        GPIO.output(in_values["front"][1], GPIO.HIGH)
        GPIO.output(in_values["back"][0], GPIO.HIGH)
    
def destroy():
    print(f"end time {datetime.now().strftime('%S.%f')[:-4]}")
    global deviations
    
    for key in pwm_pins:
        pwm_pins[key].stop()
    GPIO.cleanup() # Release all GPIO
    
    x_axis = range(len(deviations))
    plt.grid(axis='x', markevery=1)
    plt.plot(x_axis, deviations[:, 0], 'b', x_axis, deviations[:, 1], 'r')
#     plt.plot(x_axis, diff_array, 'k', x_axis, avg_diff_array, 'y', x_axis, pid_output_array, 'c', x_axis, pid_p_array, 'r', x_axis, pid_i_array, 'g', x_axis, pid_d_array, 'b')
    plt.show()
#     for i in range(len(diff_array)):
#         print(f"{i}, diff: {diff_array[i]}, pid output: {pid_output_array[i]}, pid components: {pid_p_array[i]}")

if __name__ == '__main__':     # Program entrance
    setup()
    # Collect events in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
 