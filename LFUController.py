# to calibrate the sensors, delete the calibration values file called "LFU value limits.npy"

import time
import sys
import board
import numpy as np
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c, data_rate = 3300)

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)
channels = np.array([chan0, chan1, chan2, chan3])

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

def load_calibration():
    # to recalibrate, just delete the "LFU value limits.npy" file
    # first column is low limit, second is high
    # first row is top left, second is top right, third is bottom left, fourth is bottom right
    global calib_vals
    calib_vals = np.array([[-1,-1], [-1,-1], [-1,-1], [-1,-1]])
    
    global file
    try:
        file = open(sys.path[0]+"/LFU value limits.npy", 'rb')
    except:
        calibrate()
    else:
        calib_vals = np.load(file)

# def load_calibration():
# try:
#     file = open(sys.path[0]+"/LFU value limits", 'rb')
# except:
#     file = open(sys.path[0]+"/LFU value limits", 'wb')
#     calibrate()
#     np.save(file, calib_vals)
# else:
#     calib_vals = np.load(file, allow_pickle=True)
# file.close()

def calibrate():
    file = open(sys.path[0]+"/LFU value limits.npy", 'wb')
    print_values()
    user_input = input("place LFU on black, press any key to continue...")
    for i in range(4):
        calib_vals[i][0] = channels[i].value
    user_input = input("place LFU on white, press any key to continue...")
    for i in range(4):
        calib_vals[i][1] = channels[i].value
    print_values()
    np.save(file, calib_vals)
    file.close()

def print_channel_values():
    print(f"{channels[0].value} {channels[1].value} {channels[2].value} {channels[3].value}")
    

def print_values():
    print("black values:\t{:>5}\t{:>5}\t{:>5}\t{:>5}".format(calib_vals[0,0], calib_vals[1,0], calib_vals[2,0], calib_vals[3,0]))
    print("white values:\t{:>5}\t{:>5}\t{:>5}\t{:>5}".format(calib_vals[0,1], calib_vals[1,1], calib_vals[2,1], calib_vals[3,1]))

def get_deviation():
    values = np.zeros(4)
    for i in range(4):
        values[i] = channels[i].value
    return values

if __name__ == '__main__':     # Program entrance
    load_calibration()
    while True:
        print_channel_values()
#         print(get_deviation())
        time.sleep(0.01)
else:
    load_calibration()