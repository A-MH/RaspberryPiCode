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
from pynput import keyboard
import LFUController as LFU
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
import atexit

def exit_handler():
    destroy()

atexit.register(exit_handler)

travel_distance = 5

pwm = 0

default_pwm = 100
homing_pwm = 20
pwm_acceleration = 1000 * default_pwm
pwm_deceleration = 2 * default_pwm

en_values = {"right": 20, "left": 8, "front": 25, "back": 17}

pwm_pins = {"front": None, "back": None, "left": None, "right": None}

in_values = {"right": [12, 16], "left": [1, 7], "front": [23, 24], "back": [18, 15]}

pwm_multipliers = {"front": 1, "back": 1, "left": 1, "right": 1}

end_offsets = [-12, -12, -13, -12]

deviations_padding = 6
deviations = np.ones([deviations_padding,4]) * 100000

ctrl_held = False

def on_press(key):
    global travel_direction
    global travel_distance
    global ctrl_held
    global end_offsets
    if (key == keyboard.Key.up):
        go_to_dest("left", "right", 0, 1, travel_distance, end_offsets[0], end_offsets[1])
        travel_direction = "right"
    elif(key == keyboard.Key.down):
        go_to_dest("right", "left", 3, 2, travel_distance, end_offsets[3], end_offsets[2])
        travel_direction = "forward"
    elif(key == keyboard.Key.left):
        go_to_dest("back", "front", 2, 0, travel_distance, end_offsets[2], end_offsets[0])
        travel_direction = "back"
    elif(key == keyboard.Key.right):
        go_to_dest("front", "back", 1, 3, travel_distance, end_offsets[1], end_offsets[3])
        travel_direction = "left"
    elif key == keyboard.Key.ctrl:
        print("ctrl held")
        ctrl_held = True
    elif hasattr(key, 'char'):
        if key.char == "c" and ctrl_held:
            print("ctrl-c pressed")
            destroy()
        try:
            print(f" travel_distance set to {key.char}")
            travel_distance = int(key.char)
        except:
            pass

def start_travel():
    global travel_direction
    travel_direction = "left"
    global end_offsets
    while True:
        if (travel_direction == "forward"):
            go_to_dest("left", "right", 0, 1, travel_distance, end_offsets[0], end_offsets[1])
            travel_direction = "right"
        elif(travel_direction == "back"):
            go_to_dest("right", "left", 3, 2, travel_distance, end_offsets[3], end_offsets[2])
            travel_direction = "forward"
        elif(travel_direction == "left"):
            go_to_dest("back", "front", 2, 0, travel_distance, end_offsets[2], end_offsets[0])
            travel_direction = "right"
        elif(travel_direction == "right"):
            go_to_dest("front", "back", 1, 3, travel_distance, end_offsets[1], end_offsets[3])
            travel_direction = "left"
        time.sleep(0.1)
    
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
        pwm_pins[key] = GPIO.PWM(en_values[key], 500)
        pwm_pins[key].start(0)
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.output(value[0], GPIO.LOW)
        GPIO.setup(value[1], GPIO.OUT)
        GPIO.output(value[1], GPIO.LOW)
#     listener = keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release)
#     listener.start()

def go_to_dest(rel_left, rel_right, sensor_left, sensor_right, travel_distance, offset_left, offset_right):
    global deviations
    global pwm_pins
    global pwm_multipliers
    global should_stop
    
    pwm_right = 0
    pwm_left = 0
    distance_travelled = 0
    acc_counter = 0
    dec_counter_left = 0
    dec_counter_right = 0
    dec_counter_home = 0
    dec_counter_thre = 3
    rise_threshold = 600
    destination_reached_left = False
    destination_reached_right = False
    check_for_rise = False
    check_for_junction = False
    is_accelerating = True
    GPIO.output(in_values[rel_left][0], GPIO.HIGH)
    GPIO.output(in_values[rel_right][1], GPIO.HIGH)
    old_time = datetime.now()
#     print(f"entring loop {old_time.strftime('%S.%f')[:-4]}")
    while not (destination_reached_left and destination_reached_right):
#         print("entered loop")
        if is_accelerating:
#             print("is accelerating")
            pwm_left = 100
            pwm_right = 100
            if (acc_counter > 1):
                is_accelerating = False
                if travel_distance > 2:
                    pwm_left = default_pwm
                    pwm_right = default_pwm
                else:
                    pwm_left = homing_pwm
                    pwm_right = homing_pwm
                acc_counter = 0
            else:
                acc_counter += 1
#             print("here")
        deviations = np.append(deviations, [LFU.get_deviation()], axis = 0)
        # after a junction is registered, we have to wait a bit before 
        if not (check_for_junction or check_for_rise) and \
           deviations[-1, sensor_left] - deviations[-deviations_padding, sensor_left] < 0:
#             print(f"ready for rise {datetime.now().strftime('%S.%f')[:-4]}")
            check_for_rise = True
        if check_for_rise and not check_for_junction and \
           deviations[-1, sensor_left] - deviations[-deviations_padding, sensor_left] >= rise_threshold and \
           deviations[-1, sensor_right] - deviations[-deviations_padding, sensor_right] >= rise_threshold:
#             print(f"rise registered {datetime.now().strftime('%S.%f')[:-4]}")
            check_for_rise = False
            check_for_junction = True
        if check_for_junction and \
           (deviations[-2, sensor_left] > deviations[-1, sensor_left] or deviations[-2, sensor_right] > deviations[-1, sensor_right]):
            check_for_rise = False
            check_for_junction = False
            distance_travelled += 1
            print(f"junction {distance_travelled} reached {(datetime.now() - old_time).seconds}.{(datetime.now() - old_time).microseconds}")
            old_time = datetime.now()
        if distance_travelled == travel_distance:
            if not destination_reached_left and deviations[offset_left, sensor_left] > deviations[-1, sensor_left]:
                if dec_counter_left > 0:
                    GPIO.output(in_values[rel_left][1], GPIO.LOW)
                    pwm_left = 0
                    dec_counter_left = 0
                    destination_reached_left = True
#                     print("left wheel stopping")
                else:
                    GPIO.output(in_values[rel_left][0], GPIO.LOW)
                    GPIO.output(in_values[rel_left][1], GPIO.HIGH)
                    pwm_left = 90
                    dec_counter_left += 1
            if not destination_reached_right and deviations[offset_right, sensor_right] > deviations[-1, sensor_right]:
                if dec_counter_right > 0:
                    GPIO.output(in_values[rel_right][0], GPIO.LOW)
                    pwm_right = 0
                    dec_counter_right = 0
                    destination_reached_right = True
#                     print("right wheel stopping")
                else:
                    GPIO.output(in_values[rel_right][1], GPIO.LOW)
                    GPIO.output(in_values[rel_right][0], GPIO.HIGH)
                    pwm_right = 90
                    dec_counter_right += 1
        elif travel_distance > 2 and travel_distance == distance_travelled + 1 and dec_counter_home <= dec_counter_thre:
            rise_threshold = 250
            if dec_counter_home == 0:
                GPIO.output(in_values[rel_left][0], GPIO.LOW)
                GPIO.output(in_values[rel_left][1], GPIO.HIGH)
                GPIO.output(in_values[rel_right][1], GPIO.LOW)
                GPIO.output(in_values[rel_right][0], GPIO.HIGH)
                pwm_left = 10
                pwm_right = 10
            elif dec_counter_home >= dec_counter_thre:
                GPIO.output(in_values[rel_left][1], GPIO.LOW)
                GPIO.output(in_values[rel_left][0], GPIO.HIGH)
                GPIO.output(in_values[rel_right][0], GPIO.LOW)
                GPIO.output(in_values[rel_right][1], GPIO.HIGH)
                pwm_right = homing_pwm
                pwm_left = homing_pwm
            dec_counter_home += 1
        pwm_pins[rel_left].ChangeDutyCycle(pwm_left * pwm_multipliers[rel_left])
        pwm_pins[rel_right].ChangeDutyCycle(pwm_right * pwm_multipliers[rel_right])

def destroy():
    global pwm_pins
    global deviations

    for key in pwm_pins:
        pwm_pins[key].stop()
    GPIO.cleanup() # Release all GPIO
#     print(deviations.shape)
    plt.grid(axis='x', markevery=1)
    plt.grid(axis='y', markevery=1)
    deviations = deviations[deviations_padding:]
    x_axis = range(deviations.shape[0])
    plt.plot(x_axis, deviations[:, 0], 'b', x_axis, deviations[:, 1], 'r', x_axis, deviations[:, 2], 'k', x_axis, deviations[:, 3], 'y')
#     plt.plot(x_axis, diff_array, 'k', x_axis, avg_diff_array, 'y', x_axis, pid_output_array, 'c', x_axis, pid_p_array, 'r', x_axis, pid_i_array, 'g', x_axis, pid_d_array, 'b')
    plt.show()
#     for i in range(len(diff_array)):
#         print(f"{i}, diff: {diff_array[i]}, pid output: {pid_output_array[i]}, pid components: {pid_p_array[i]}")

if __name__ == '__main__':     # Program entrance
    setup()
    global travel_direction
    travel_direction = "forward"
    try:
        start_travel()
    except KeyboardInterrupt:
        destroy()
