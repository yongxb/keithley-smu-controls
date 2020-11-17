# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 13:40:04 2018

@author: Home
"""

# Import necessary packages
from pymeasure.instruments.keithley import Keithley2400
#import numpy as np
import pandas as pd
from time import sleep, asctime

# Set the input parameters
data_points = 24*60
no_of_points_per_file = 60
file_count = 0
currents = []
voltages = []
times = []

# Connect and configure the instrument
sourcemeter = Keithley2400("ASRL6::INSTR")
print(sourcemeter.id)

sourcemeter.apply_voltage()
sourcemeter.compliance_current = 105e-3
sourcemeter.source_voltage = 50
sourcemeter.enable_source()

for i in range(data_points):
    current1 = sourcemeter.current
    voltages.append(current1[0])
    currents.append(current1[1])
    times.append(asctime())
    sleep(60)
    if(len(voltages) >= no_of_points_per_file):
        data = pd.DataFrame({
            'Voltage (V)': voltages,
            'Current (A)': currents,
            'Time': times
        })

        data.to_csv('.\\keithley_readings\\keithley_readings_' + str(file_count) + '.csv')
        voltages = []
        currents = []
        times = []
        file_count = file_count + 1
    

# Save the data columns in a CSV file
data = pd.DataFrame({
    'Voltage (V)': voltages,
    'Current (A)': currents,
    'Time': times
})

data.to_csv('.\\keithley_readings\\keithley_readings_' + str(file_count) + '.csv')

sourcemeter.shutdown()