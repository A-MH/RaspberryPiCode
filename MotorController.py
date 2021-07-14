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

sample_time = 0.005

is_accelerating = True
is_decelerating = False

pwm = 0

wd = 21.5 # wheel distance (distance between two opposite wheels
   
default_pwm = 13
pwm_acceleration = 1000 * default_pwm
pwm_deceleration = 2 * default_pwm

en_values = {"front": 20, "back": 8, "left": 25, "right": 17}

pwm_pins = {"front": None, "back": None, "left": None, "right": None}

in_values = {"front": [16, 12], "back": [7, 1], "left": [24, 23], "right": [15, 18]}

pwm_multipliers = {"front": 1, "back": 1, "left": 1, "right": 1}

travel_direction = None
old_travel_direction = None
diff_array = []
avg_diff_array = []
pid_p_array = []
pid_i_array = []
pid_d_array = []
pid_output_array = []
deviation0 = []
deviation2 = []


def on_press(key):
    global travel_direction
    try:
        if (key == keyboard.Key.up):
            travel_direction = "forward"
        elif(key == keyboard.Key.down):
            travel_direction = "back"
        elif(key == keyboard.Key.right):
            travel_direction = "right"
        elif(key == keyboard.Key.left):
            travel_direction = "left"
        else:
            travel_direction = None
    except AttributeError:
        travel_direction = None
    print('key {0} pressed'.format(key))

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

def setup():
    global pwm_pins
    global pwm_values
    for key, value in in_values.items():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(en_values[key], GPIO.OUT) 
        pwm_pins[key] = GPIO.PWM(en_values[key], 200) 
        pwm_pins[key].start(0)
        GPIO.setup(value[0], GPIO.OUT)
        GPIO.output(value[0], GPIO.LOW)
        GPIO.setup(value[1], GPIO.OUT)
        GPIO.output(value[1], GPIO.LOW)

def SetWheelV(pwm_far, pwm_near, pwm_l1, pwm_l2, diff):
    global pwm
    global diff_array
    global avg_diff_array
    global pid_p_array
    global pid_i_array
    global pid_d_array
    global pid_output_array
    global pid
    global is_accelerating
    global is_decelerating
    global travel_direction
    global old_travel_direction
    global is_new_direction
    global counter
    
    avg_diff = diff
    n_average = 3
    if (len(diff_array) >= n_average - 1):
        value_sum = 0
        for i in range(n_average - 1):
            value_sum = value_sum + diff_array[-i - 1]
        avg_diff = (diff + value_sum) / n_average
    avg_diff_array.append(avg_diff)
    diff_array.append(diff)
#     pwm = default_pwm
    if is_accelerating:
        pwm = pwm + pwm_acceleration
        if pwm >= 80:
            pwm = 80
            if (counter > 2):
                is_accelerating = False
                pwm = default_pwm
                counter = 0
            counter = counter + 1
    elif is_decelerating:
        pwm = pwm - pwm_deceleration
        if pwm <= 0:
            is_decelerating = False
            is_accelerating = True
            old_travel_direction = travel_direction
            is_new_direction = True
            pwm = 0
#     print(control)
    global pwm_pins
    global pwm_multipliers
#     print("diff: {}".format(diff))
    pid_output = pid(avg_diff_array[-1])
    pid_p_array.append(pid.components[0])
    pid_i_array.append(pid.components[1])
    pid_d_array.append(pid.components[2])
    pid_output_array.append(pid_output)
#     print("control: {}".format(control))
    pid_output = abs(pid_output)
    pid_output = 0
    pwm_values_temp = {
        "far": pwm,
        "near": round(pwm * (1 - pid_output)),
        "lateral": 0
        }
    if (pwm_values_temp["near"] < 0):
        pwm_values_temp["near"] = 0
    if (pwm_values_temp["far"] - pwm_values_temp["near"]) != 0:
        Df = wd * pwm / (pwm - pwm_values_temp["near"])
        Dtv = wd / 2
        Dth = Df - wd / 2
        Dt = math.sqrt(Dtv**2 + Dth**2)
        pwm_values_temp["lateral"] = math.sin(math.atan(Dtv / Dth)) * Dt * (pwm - pwm_values_temp["near"]) / wd
        # wheels will only start turning for values above 6, the ollowing formula just adds a little bit to lower values to above 6
#         pwm_values_temp["lateral"] = pwm_values_temp["lateral"] + 5 / pwm_values_temp["lateral"]**0.2
    pwm_pins[pwm_far].ChangeDutyCycle(pwm_values_temp["far"] * pwm_multipliers[pwm_far])
    pwm_pins[pwm_near].ChangeDutyCycle(pwm_values_temp["near"] * pwm_multipliers[pwm_near])
    pwm_pins[pwm_l1].ChangeDutyCycle(pwm_values_temp["lateral"] * pwm_multipliers[pwm_l1])
    pwm_pins[pwm_l2].ChangeDutyCycle(pwm_values_temp["lateral"] * pwm_multipliers[pwm_l2])


stopping_junction = 1
current_junction = 0
junction_registered = False
should_stop = False
counter = 0

def UpdateInValues():
    global deviation0
    global deviation2
    while True:
        global pid
        global pwm
        global pwm_pins
        global old_travel_direction
        global travel_direction
        global is_decelerating
        global is_new_direction
        
        global current_junction
        global stopping_junction
        global should_stop
        global junction_registered
        global counter
#         await asyncio.sleep(sample_time)
#         print("update wait")

        deviation = LFU.get_deviation()
#         print(deviation)   
        if travel_direction != old_travel_direction:
            GPIO.output(in_values["left"][0], GPIO.LOW)
            GPIO.output(in_values["left"][1], GPIO.LOW)
            GPIO.output(in_values["right"][0], GPIO.LOW)
            GPIO.output(in_values["right"][1], GPIO.LOW)
            GPIO.output(in_values["front"][0], GPIO.LOW)
            GPIO.output(in_values["front"][1], GPIO.LOW)
            GPIO.output(in_values["back"][0], GPIO.LOW)
            GPIO.output(in_values["back"][1], GPIO.LOW)
            old_travel_direction = travel_direction
            is_new_direction = True
#             if old_travel_direction != None:
#                 is_decelerating = True
        if (old_travel_direction == "forward"):
            left_dev = 0.7
            right_dev = 0.6
            deviation0.append(deviation[0])
            deviation2.append(deviation[1])
            if is_new_direction == True:
                pid = PID(Kp=0.7, Ki = 0, Kd = 0.2, setpoint=0,sample_time=sample_time, output_limits=(-1, 1))
                is_new_direction = False
            if not junction_registered and (deviation[0] > left_dev or deviation[1] > right_dev):
                junction_registered = True
                current_junction = current_junction + 1
                if current_junction == stopping_junction:
                    should_stop = True
            if junction_registered and deviation[0] < left_dev and deviation[1] < right_dev:
                junction_registered = False
            if should_stop:
#                 pass
                if deviation0[-4] > deviation0[-1]:
                    GPIO.output(in_values["left"][0], GPIO.LOW)
                if deviation2[-4] > deviation2[-1]:
                    GPIO.output(in_values["right"][0], GPIO.LOW)
                if deviation0[-4] > deviation0[-1] and deviation2[-4] > deviation2[-1]:
                    travel_direction = "back"
                    old_travel_direction = None
                    current_junction = 0
                    should_stop = False
#                 print("stopped")
            else:
                GPIO.output(in_values["left"][0], GPIO.HIGH)
                GPIO.output(in_values["right"][0], GPIO.HIGH)
                diff = deviation[0] - deviation[1]
                diff = 0
                if (diff < 0):
                    GPIO.output(in_values["front"][0], GPIO.HIGH)
                    GPIO.output(in_values["back"][1], GPIO.HIGH)
                    SetWheelV("left", "right", "front", "back", diff)
                else:
                    GPIO.output(in_values["front"][1], GPIO.HIGH)
                    GPIO.output(in_values["back"][0], GPIO.HIGH)
                    SetWheelV("right", "left", "front", "back", diff)
        elif (old_travel_direction == "back"):
            if counter > 5:
                GPIO.output(in_values["left"][1], GPIO.LOW)
                GPIO.output(in_values["right"][1], GPIO.LOW)
                travel_direction = None
                old_travel_direction = None
                counter = 0
            else:
                counter = counter + 1
                if is_new_direction == True:
                    pid = PID(Kp=0.7, Ki = 0, Kd = 0.2, setpoint=0,sample_time=sample_time, output_limits=(-1, 1))
                    is_new_direction = False
                GPIO.output(in_values["left"][1], GPIO.HIGH)
                GPIO.output(in_values["right"][1], GPIO.HIGH)
                diff = deviation[2] - deviation[3]
                diff = 0
                if (diff < 0):
                    GPIO.output(in_values["front"][1], GPIO.HIGH)
                    GPIO.output(in_values["back"][0], GPIO.HIGH)
                    SetWheelV("left", "right", "front", "back", diff)
                else:
                    GPIO.output(in_values["front"][0], GPIO.HIGH)
                    GPIO.output(in_values["back"][1], GPIO.HIGH)
                    SetWheelV("right", "left", "front", "back", diff)
        elif (old_travel_direction == "left"):
            if is_new_direction == True:
                pid = PID(Kp = 1.1, Ki = 0, Kd = 0.05, setpoint=0,sample_time=sample_time, output_limits=(-1, 1))
                is_new_direction = False
            GPIO.output(in_values["front"][1], GPIO.HIGH)
            GPIO.output(in_values["back"][1], GPIO.HIGH)
            diff = deviation[0] - deviation[2]
            diff = 0
            if (diff < 0):
                GPIO.output(in_values["left"][1], GPIO.HIGH)
                GPIO.output(in_values["right"][0], GPIO.HIGH)
                SetWheelV("front", "back", "left", "right", diff)
            else:
                GPIO.output(in_values["left"][0], GPIO.HIGH)
                GPIO.output(in_values["right"][1], GPIO.HIGH)
                SetWheelV("back", "front", "left", "right", diff)
        elif (old_travel_direction == "right"):
            if is_new_direction == True:
                pid = PID(Kp = 0.7, Ki = 0, Kd = 0.1, setpoint=0,sample_time=sample_time, output_limits=(-1, 1))
                is_new_direction = False
            GPIO.output(in_values["front"][0], GPIO.HIGH)
            GPIO.output(in_values["back"][0], GPIO.HIGH)
            diff = deviation[1] - deviation[3]
            diff = 0
            if (diff < 0):
                GPIO.output(in_values["left"][0], GPIO.HIGH)
                GPIO.output(in_values["right"][1], GPIO.HIGH)
                SetWheelV("front", "back", "left", "right", diff)
            else:
                GPIO.output(in_values["left"][1], GPIO.HIGH)
                GPIO.output(in_values["right"][0], GPIO.HIGH)
                SetWheelV("back", "front", "left", "right", diff)

async def move():
#     task_get_key_press = asyncio.create_task(GetKeyPress())
    task_update_in_values = asyncio.create_task(UpdateInValues())
    await task_update_in_values

def destroy():
    global avg_diff_array
    global diff_array
    global pid_output_array
    global pid_p_array
    global pid_i_array
    global pid_d_array
    global deviation0
    global deviation2
    
    for key in pwm_pins:
        pwm_pins[key].stop()
    GPIO.cleanup() # Release all GPIO
    
    x_axis = range(len(deviation0))
    plt.grid(axis='x', markevery=1)
    plt.plot(x_axis, deviation0, 'b', x_axis, deviation2, 'r')
#     plt.plot(x_axis, diff_array, 'k', x_axis, avg_diff_array, 'y', x_axis, pid_output_array, 'c', x_axis, pid_p_array, 'r', x_axis, pid_i_array, 'g', x_axis, pid_d_array, 'b')
    plt.show()
#     for i in range(len(diff_array)):
#         print(f"{i}, diff: {diff_array[i]}, pid output: {pid_output_array[i]}, pid components: {pid_p_array[i]}")

if __name__ == '__main__':     # Program entrance
    setup()
    try:
#         asyncio.run(move())
        UpdateInValues()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()