from enum import Enum
import numpy as np
import LFUController as lfu
import NetworkManager as nm
import MotorController as mc
import CameraManager as cm
import ArmController as ac
import LiftController as lc
import time
from datetime import datetime

def setup():
#     nm.setup_connection(rs.ID)
    pass

def format_commands(command_str):
    global commands
    commands = []
    command_type = ''
    parameter = ''
    parameters = []
    char_is_com = True # is the following character part of the command or parameter
    for char in command_str:
        if char == ' ': # if character is a space then following characters are part of parameter
            # if char_is_com is not true it means it is a parameter
            if not char_is_com:
                parameters.append(float(parameter))
            parameter = ''
            char_is_com = False
        # if character is a semi-colon then following characters are part of command. also the comand parameter pair should be added to commands array
        elif char == ',':
            parameters.append(float(parameter))
            # if there is only one parameter, then save it as a numerical instead of a list of size one
            if len(parameters) > 1:
                commands.append([command_type, parameters])
            else:
                commands.append([command_type, float(parameter)])
            command_type = ''
            parameter = ''
            parameters = []
            char_is_com = True
        elif char_is_com:
           command_type += char
        else:
           parameter += char

def run_commands():
#     ac.prepare_syringe()
#     time.sleep(5)
    global bounce_durations
    global commands
    syringe_weight = -1
    old_time = datetime.now()
    bounce_durations = []
    while True:
#         commands_str = nm.get_commands()
#         commands_str = "loadf 5 20.29 0,loadf 5 19.3 0,loadf 5 19.3 0,loadf 4 19.3 0,"
        commands_str = "refill 0 0,"
        bounce_durations.append((datetime.now() - old_time).seconds)
#         print(f"time taken: {(datetime.now() - old_time).seconds}")
        old_time = datetime.now()
        time.sleep(1)
        format_commands(commands_str)
        print(f"commands: {commands}")
        for i in range(len(commands)):
            command_type = commands[i][0]
            if command_type == 'loadf':
                if i == 0:
                    syringe_weight = commands[i][1][1]
                print(f"syringe weight actual: {syringe_weight}")
                actual_loaded, dead_weight = load_f(commands[i][1][0], syringe_weight, commands[i][1][2])
                syringe_weight -= actual_loaded
#                 syringe_weight_actual = commands[i][1][1] - commands[i][1][0]
#                 dead_weight = 0.8
#                 nm.send_result(f"{syringe_weight_actual} {dead_weight}")
#                 print(f"sent: {syringe_weight_actual} {dead_weight}")
            elif command_type == 'loadvg' or command_type == 'loadpg':
                result = load_b(command_type, commands[i][1])
                nm.send_result(result);
            elif command_type == 'refill':
                print("command is refill")
                result = refill(commands[i][1][0], commands[i][1][1])
        break
            
def load_b(command_type, amount):
    print("loading b")
    extend_duration = 0.73
    flow_rate = 6.8 # assuming it is PG initially
    if command_type == "loadvg": # if it's VG, then adjust flowrate
        flow_rate = 5
    amount_added = 0
    orig_weight = cm.get_weight()
    min_amount = 0.62
    while amount_added < 0.95 * amount:
        load_time = (amount - amount_added - min_amount) / flow_rate 
        load_time = 0 if load_time < 0 else load_time
        print(load_time)
        ac.extend(extend_duration)
        time.sleep(load_time)
        ac.retract(100)
        time.sleep(extend_duration + 0.2)
        amount_added = cm.get_weight() - orig_weight
        if amount_added/amount > 1.2:
            print(f"too much {command_type[-2:]} added, {amount_added*100/amount}% added")
        elif amount_added/amount < 0.95:
            print(f"too little {command_type[-2:]} added, {amount_added*100/amount}% filled")
    print(f"{amount_added}g added. target: {amount}g")
    return "ok"
    
def load_f(target_weight, syringe_weight, dead_weight):
    orig_weight = cm.get_weight()
    curr_weight_adjusted = 0
    ac.enable_magnet()
    sleep_time_extend = ac.extend(syringe_weight=syringe_weight + dead_weight)
    time.sleep(sleep_time_extend)
    ac.stop_arm()
    if target_weight <= 0.1:
        ac.extend()
        time.sleep(0.2)
        ac.stop_arm()
        dead_weight += 1.05
        wasted_pull = 0.6
    else:
        wasted_pull = 0.4
    while target_weight > 0.1 and curr_weight_adjusted < round(target_weight * 0.95, 2) or\
          target_weight <= 0.1 and curr_weight_adjusted < round(target_weight * 0.8, 2):
        sleep_time = ac.retract_fill(target_weight - curr_weight_adjusted + wasted_pull)
        time.sleep(sleep_time)
        ac.stop_arm()
        wasted_pull = 0
        if target_weight - curr_weight_adjusted <= 0.1:
            if target_weight - curr_weight_adjusted <= 0.03:
                time.sleep(2)
            time.sleep(1.5)
        time.sleep(2)
        current_weight = cm.get_weight()
#         current_weight = target_weight + orig_weight
        curr_weight_adjusted = round(current_weight - orig_weight, 2)
        print(f"current weight: {curr_weight_adjusted}")
    ac.disable_magnet()
    ac.retract(100)
    print(f'target weight reached: {curr_weight_adjusted}g')
    time.sleep(sleep_time_extend)
    return (curr_weight_adjusted, dead_weight)
    
def refill(syringe_weight, dead_weight):
    container_weight = 15 # weight of empty container
    conc_weight = cm.get_weight() - container_weight # weight of concentrate
#     conc_weight = 96.5 - container_weight # weight of concentrate
    print(f"container weight before load: {conc_weight + container_weight}")
    conc_weight_unavailabe = 7
    conc_percentage_available = 1
    if conc_weight < ac.syringe_weight_full - syringe_weight:
        conc_percentage_available = 1 - conc_weight_unavailabe / conc_weight
    # bring container in contact with syringe tip
    sleep_time_phase1_lift = lc.extend_phase1(conc_weight)
    sleep_time_phase1_arm = ac.extend(syringe_weight=syringe_weight)
    # depending on which arm reaches destination first, 
    if sleep_time_phase1_arm > sleep_time_phase1_lift:
        time.sleep(sleep_time_phase1_lift)
        lc.stop_lift()
        time.sleep(sleep_time_phase1_arm - sleep_time_phase1_lift)
        ac.stop_arm()
    else:
        time.sleep(sleep_time_phase1_arm)
        ac.stop_arm()
        time.sleep(sleep_time_phase1_lift - sleep_time_phase1_arm)
        lc.stop_lift()
    ac.enable_magnet()
    sleep_time, refill_rate = ac.extend_refill(syringe_weight, conc_percentage_available)
    lc.extend_phase2(refill_rate)
    time.sleep(sleep_time)
    ac.disable_magnet()
    lc.stop_lift()
    ac.retract()
    lc.retract()
    time.sleep(10)
    print(f"Syringe weight refilled: {conc_weight - cm.get_weight() + container_weight}")

def destroy():
    global bounce_durations
    durations_count = [0,0,0,0,0]
    for duration in bounce_durations:
        if duration >= 24:
            durations_count[4] += 1
        elif duration >= 12:
            durations_count[3] += 1
        elif duration >= 6:
            durations_count[2] += 1
        elif duration > 3:
            durations_count[1] += 1
        else:
            durations_count[0] += 1
    print(f"durations count: {durations_count}")
    ac.destroy()

setup()
run_commands()

