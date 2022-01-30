# to calibrate the sensors, delete the calibration values file called "LFU value limits.npy"

import time
import sys
import board
import numpy as np
import busio
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = I2C(3)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c, data_rate = 3300)

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)

if __name__ == '__main__':     # Program entrance
    while True:
        print(format(chan0.value/1000, ".2f"))
        time.sleep(0.5)
