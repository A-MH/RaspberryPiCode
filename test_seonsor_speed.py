# to calibrate the sensors, delete the calibration values file called "LFU value limits.npy"

from datetime import datetime
import time
import sys
import board
import numpy as np
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c, data_rate = 3300)
ads.mode = Mode.CONTINUOUS
# Create single-ended input on all channels
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)
channels = np.array([chan0, chan1, chan2, chan3])


# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

def print_values():
    print("black values:\t{:>5}\t{:>5}\t{:>5}\t{:>5}".format(calib_vals[0,0], calib_vals[1,0], calib_vals[2,0], calib_vals[3,0]))
    print("white values:\t{:>5}\t{:>5}\t{:>5}\t{:>5}".format(calib_vals[0,1], calib_vals[1,1], calib_vals[2,1], calib_vals[3,1]))

values = np.zeros([0, 4])
def get_readings():
    global values
    readings = np.zeros(4)
    print(f"entring loop {datetime.now().strftime('%S.%f')[:-4]}")
    for i in range(1000):
        for j in range(4):
            readings[j] = channels[j].value
        values = np.append(values, [readings], axis = 0)
    print(f"exiting loop {datetime.now().strftime('%S.%f')[:-4]}")
    print(f"readings: {values.shape[0]}")

get_readings()
