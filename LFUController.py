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
ads = ADS.ADS1015(i2c)

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)
channels = np.array([chan0, chan1, chan2, chan3])

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

def load_calibration():
    # first column is low limit, second is high
    global calib_vals
    global file
    calib_vals = np.array([[-1,-1], [-1,-1], [-1,-1], [-1,-1]])
    try:
        file = open(sys.path[0]+"/LFU value limits", 'rb')
    except:
        calibrate()
    else:
        calib_vals = np.load(file)
    print(calib_vals)

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
    file = open(sys.path[0]+"/LFU value limits", 'wb')
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

def print_values():
    print("black values:\t{:>5}\t{:>5}\t{:>5}\t{:>5}".format(calib_vals[0,0], calib_vals[1,0], calib_vals[2,0], calib_vals[3,0]))
    print("white values:\t{:>5}\t{:>5}\t{:>5}\t{:>5}".format(calib_vals[0,1], calib_vals[1,1], calib_vals[2,1], calib_vals[3,1]))

def get_deviation():
    values = np.zeros(4)
    for i in range(4):
        values[i] = channels[i].value
    deviation = (values - calib_vals[:,1]) / (calib_vals[:,0] - calib_vals[:,1])
    return deviation


if __name__ == '__main__':     # Program entrance
    load_calibration()
    while True:
        get_deviation()
        time.sleep(0.01)
else:
    load_calibration()