from enum import Enum
import numpy as np
import LFUController as lfu
import NetworkManager as nm
import MotorController as mc
import CameraManager as cm
import ArmController as ac
import time

ID = 1

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
        # if character is a dash then following characters are part of command. also the comand parameter pair should be added to commands array
        elif char == '-':
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
    commands_str = nm.get_commands_str(ID)
    format_commands(commands_str)
    print(f"commands: {commands}")
    for i in range(len(commands)):
        target_weight = commands[i][1][0]
        print(f"\ntarget weight: {target_weight}")
        syringe_weight = commands[i][1][1]
        ac.enable_magnet()
        ac.extend(syringe_weight)
        current_weight = cm.read_scale()
        old_weight = current_weight
        curr_weight_adjusted = 0
        dead_time = 0
        while curr_weight_adjusted < target_weight * 0.95:
            ac.loadf(target_weight - curr_weight_adjusted + dead_time)
            dead_time = 0
            if target_weight < 0.3:
                time.sleep(1)
            time.sleep(2)
            print(f"current weight: {curr_weight_adjusted}")
            current_weight = cm.read_scale()
            curr_weight_adjusted = current_weight - old_weight
        print(f'loaded {curr_weight_adjusted}g')
        ac.disable_magnet()
#         syringe_weight -= current_weight
        ac.retract(100)
        print('target weight reached/n')
        if i + 1 < len(commands):
            commands[i+1][1][1] = syringe_weight - curr_weight_adjusted
        time.sleep(ac.duration_limits[1])
            
def destroy():
    ac.destroy()

try:
    run_commands()
except KeyboardInterrupt:
    destroy()
#     mc.start_travel(command[0], command[1])

