from enum import Enum
import numpy as np
import LFUController as lfu
import NetworkManager as nm

ID = 1

class MoveDirection(Enum):
    EAST=1
    NORTH=2
    WEST=3
    SOUTH=4

def break_subroute(subroute):
    commands = []
    command = ''
    for char in subroute:
        if char!='-':
           command += char
        else:
            commands.append(command)
            command = ''
    return commands

# while True:
subroute = nm.get_subroute(ID)
commands = break_subroute(subroute)
print(commands)
for command in commands:
    if command=='w':
