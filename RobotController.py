import asyncio
from enum import Enum
import numpy as np
import LFUController as lfu
import NetworkManager as nm
import MotorController as mc
import CameraManager as cm
import ArmController as ac
import LiftController as lc
import RobotSpecific as rs
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

async def run_commands():
#     ac.prepare_syringe()
#     time.sleep(5)
    global bounce_durations
    global commands
    syringe_weight = -1
    old_time = datetime.now()
    bounce_durations = []
    while True:
        # commands_str = nm.get_commands()
#         commands_str = "loadf 5 20.65,loadf 0.05 19.3,loadf 0.05 19.3,loadf 0.05 19.3,loadf 0.05 19.3,loadf 0.05 19.3,"
        commands_str = "refill 15 15.47,"
        bounce_durations.append((datetime.now() - old_time).seconds)
#         print(f"time taken: {(datetime.now() - old_time).seconds}")
        old_time = datetime.now()
        time.sleep(1)
        format_commands(commands_str)
        print(f"commands: {commands}")
        for i in range(len(commands)):
            command_type = commands[i][0]
            if command_type == 'loadf':
                actual_loaded, positional_weight = await load_f(commands[i][1][0], commands[i][1][1])
                # the following conditional is only a helper for testing and should be removed for production stage
                if i < len(commands) - 1:
                    commands[i+1][1][1] = positional_weight
#                 return actual_loaded, positional_weight
            elif command_type == 'loadvg' or command_type == 'loadpg':
                result = load_b(command_type, commands[i][1])
                nm.send_result(result);
            elif command_type == 'refill':
                print("command is refill")
                syringe_weight, positional_weight = await refill(commands[i][1][0], commands[i][1][1])
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
    
async def load_f(target_weight, positional_weight):
    orig_weight = cm.get_weight()
    curr_weight_adjusted = 0
    ac.enable_magnet()
    wasted_push = 0
    friction_break_weight = 0
    if target_weight <= 0.1:
        if target_weight < 0.05:
            target_weight = 0.05
        wasted_push = 0.15
        friction_break_weight = 0.6
    await ac.extend(weight=positional_weight + friction_break_weight, homing_pwm = 100)
    while target_weight > 0.1 and curr_weight_adjusted < round(target_weight * 0.95, 2) or\
          target_weight <= 0.1 and curr_weight_adjusted < round(target_weight * 0.8, 2):
        positional_weight = await ac.retract_fill(target_weight - curr_weight_adjusted + wasted_push)
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
    await ac.retract()
    print(f'target weight reached: {curr_weight_adjusted}g')
    print(f'positional weight: {positional_weight}g')
    return curr_weight_adjusted, positional_weight
    
async def refill(syringe_weight, positional_weight):
    container_weight = 23.32 # weight of empty container
    conc_weight = cm.get_weight() - container_weight # weight of concentrate
#     conc_weight = 96.5 - container_weight # weight of concentrate
    print(f"container weight before load: {conc_weight + container_weight}")
    conc_weight_unavailabe = 3
    conc_weight_available = conc_weight + syringe_weight - conc_weight_unavailabe
    # bring container in contact with syringe tip
    task1 = asyncio.create_task(lc.extend_phase1(conc_weight + syringe_weight))
    task2 = asyncio.create_task(ac.extend(positional_weight))
    await task1
    await task2
    ac.enable_magnet()
    # then empty the remaning content of syringe
    await ac.retract_fill(positional_weight)
    # The following sleep might not be neccessary
    time.sleep(0.1)
    task1 = asyncio.create_task(lc.extend_phase2(conc_weight_available))
    task2 = asyncio.create_task(ac.extend_refill(conc_weight_available))
    await task1
    positional_weight = await task2
    lc.retract()
    ac.disable_magnet()
    await ac.retract()
    time.sleep(3)
    lc.stop_lift()
    actual_weight_syringe = conc_weight - cm.get_weight() + container_weight + syringe_weight
    print(f"Syringe weight refilled: {actual_weight_syringe}")
    print(f"Positional Weight: {positional_weight}")
    return actual_weight_syringe, positional_weight

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
asyncio.run(run_commands())

