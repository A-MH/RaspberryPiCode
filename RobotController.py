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
    for command in commands:
        target_weight = command[1][0]
        Syringe_weight = command[1][1]
        ac.enable_magnet()
        ac.extend(Syringe_weight)
        current_weight = cm.read_scale()
        old_weight = current_weight
        current_pwm = 40
        old_pwm = 100 # by setting old pwm to 100, we make sure that old and new value are not the same, and therefore ac.retract gets called in the while lopp
        while current_weight - old_weight < target_weight:
            if target_weight - current_weight < 0.5:
                current_pwm = 20
            elif target_weight - current_weight < 3:
                current_pwm = 30
            else:
                current_pwm = 40
            if not old_pwm == current_pwm:
                ac.retract(current_pwm)
            current_weight = cm.read_scale()
            old_pwm = current_pwm
        print(f'loaded {current_weight - old_weight}g')
        ac.disable_magnet()
        Syringe_weight -= current_weight
        ac.retract(100)
        print('target weight reached/n')
        time.sleep(ac.duration_limits[1])
            
def destroy():
    ac.destroy()

try:
    run_commands()
except KeyboardInterrupt:
    destroy()
#     mc.start_travel(command[0], command[1])

