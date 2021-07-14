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
import LFUController as LFU
import asyncio
from simple_pid import PID
import matplotlib.pyplot as plt
import numpy as np

travel_distance = 7

is_accelerating = True
is_decelerating = False

pwm = 0

wd = 21.5 # wheel distance (distance between two opposite wheels
   
default_pwm = 15
pwm_acceleration = 1000 * default_pwm
pwm_deceleration = 2 * default_pwm

en_values = {"front": 20, "back": 8, "left": 25, "right": 17}

pwm_pins = {"front": None, "back": None, "left": None, "right": None}

in_values = {"front": [16, 12], "back": [1, 7], "left": [24, 23], "right": [18, 15]}

pwm_multipliers = {"front": 1, "back": 1, "left": 1, "right": 1}

end_offsets = [-4, -2, -4, -2]

deviations = np.zeros([0,4])

ctrl_held = False

def on_press(key):
    global travel_direction
    global ctrl_held
    global end_offsets
    if (key == keyboard.Key.up):
        go_to_dest("left", "right", 0, 1, travel_distance, end_offsets[0], end_offsets[1])
    elif(key == keyboard.Key.down):
        go_to_dest("right", "left", 2, 3, travel_distance, end_offsets[2], end_offsets[3])
    elif(key == keyboard.Key.left):
        go_to_dest("back", "front", 0, 2, travel_distance, end_offsets[0], end_offsets[2])
    elif(key == keyboard.Key.right):
        go_to_dest("front", "back", 1, 3, travel_distance, end_offsets[1], end_offsets[3])
    elif key == keyboard.Key.ctrl:
        print("ctrl held")
        ctrl_held = True
    elif key.char == "c" and ctrl_held:
        print("ctrl-c pressed")
        destroy()

def on_release(key):
    global ctrl
    if key == keyboard.Key.ctrl:
        print("ctrl released")
        ctrl_held = False

def setup():
    GPIO.setmode(GPIO.BCM)
    global pwm_pins
    global pwm_values
    for key, value in in_values.items():
        GPIO.setup(en_values[key], GPIO.OUT) 
        pwm_pins[key] = GPIO.PWM(en_values[key], 200) 
        pwm_pins[key].start(0)
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.output(value[0], GPIO.LOW)
        GPIO.setup(value[1], GPIO.OUT)
        GPIO.output(value[1], GPIO.LOW)

def go_to_dest(rel_left, rel_right, sensor_left, sensor_right, travel_distance, offset_left, offset_right):
    global deviations
    global pwm_pins
    global pwm_multipliers
    global pwm
    global should_stop
    
    junction_registered = False
    deviation = []
    distance_travelled = 0
    counter = 0
    deviation_thre = 0.7
    destination_reached = False
    is_accelerating = True
    is_decelerating = False
    should_stop = False
    
    GPIO.output(in_values["left"][0], GPIO.LOW)
    GPIO.output(in_values["left"][1], GPIO.LOW)
    GPIO.output(in_values["right"][0], GPIO.LOW)
    GPIO.output(in_values["right"][1], GPIO.LOW)
    GPIO.output(in_values["front"][0], GPIO.LOW)
    GPIO.output(in_values["front"][1], GPIO.LOW)
    GPIO.output(in_values["back"][0], GPIO.LOW)
    GPIO.output(in_values["back"][1], GPIO.LOW)
    
    GPIO.output(in_values[rel_left][0], GPIO.HIGH)
    GPIO.output(in_values[rel_right][1], GPIO.HIGH)
    
    while not destination_reached:
#         print("entered loop")
        deviation = LFU.get_deviation()
        deviations = np.append(deviations, [deviation], axis = 0)
        # check to see if we are at a junction. if so register it
        if not junction_registered and (deviation[sensor_left] >= deviation_thre and deviation[sensor_right] >= deviation_thre):
            junction_registered = True
            distance_travelled = distance_travelled + 1
#             print(f"j{distance_travelled} registered")
            if distance_travelled == travel_distance:
#                 print("should stop")
                should_stop = True
                distance_travelled = 0
        # check if we are exiting a junction. if so register it
        if junction_registered and deviation[sensor_left] < deviation_thre and deviation[sensor_right] < deviation_thre:
            junction_registered = False
        # if we have reached the destination
        if should_stop:
            # check for the relative left sensor
            if deviations[offset_left, sensor_left] > deviations[-1, sensor_left]:
                GPIO.output(in_values[rel_left][0], GPIO.LOW)
            # check for the relative right sensor
            if deviations[offset_right, sensor_right] > deviations[-1, sensor_right]:
                GPIO.output(in_values[rel_right][1], GPIO.LOW)
            if deviations[offset_left, sensor_left] > deviations[-1, sensor_left] and deviations[offset_right, sensor_right]  > deviations[-1, sensor_right]:
                is_decelerating = True
                distance_travelled = 0
                should_stop = False
        
        if is_accelerating:
#             print("is accelerating")
            pwm = 80
            if (counter > 1):
                is_accelerating = False
                pwm = default_pwm
                counter = 0
            else:
                counter = counter + 1
        elif is_decelerating:
            GPIO.output(in_values[rel_left][0], GPIO.LOW)
            GPIO.output(in_values[rel_right][1], GPIO.LOW)
            GPIO.output(in_values[rel_left][1], GPIO.HIGH)
            GPIO.output(in_values[rel_right][0], GPIO.HIGH)
            pwm = 100
            if counter > 0:
                GPIO.output(in_values[rel_left][1], GPIO.LOW)
                GPIO.output(in_values[rel_right][0], GPIO.LOW)
                is_decelerating = False
                is_accelerating = True
                pwm = 0
                counter = 0
                destination_reached = True
            else:
                counter = counter + 1
        pwm_pins[rel_left].ChangeDutyCycle(pwm * pwm_multipliers[rel_left])
        pwm_pins[rel_right].ChangeDutyCycle(pwm * pwm_multipliers[rel_right])

def destroy():
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