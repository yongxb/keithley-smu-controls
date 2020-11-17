# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 13:40:04 2018

@author: Home
"""

# Import necessary packages
from pymeasure.instruments.keithley import Keithley2400
#import numpy as np
import pandas as pd
from time import sleep, asctime, localtime, time

#### Input parameters
data_points = 0
no_of_points_per_file = 30

time_delay = 120 # in seconds

is_source_current = False
source_current = 200e-6 # in A
voltage_limit = 210 # in V

is_source_voltage = True
source_voltage = 150 # in V
current_limit = 1.05 # in A

#### Save file location/name
csv_name = '17April2019_' ## Need to change

#### Initialize list ####
currents = []
voltages = []
times = []

#### Counters ####
counter = 0
file_count = 0
time_counter = 1
save_count = 1

# Connect and configure the instrument
#sourcemeter = Keithley2400("USB0::0x05E6::0x2450::04373013::INSTR")
try:
    sourcemeter = Keithley2400("ASRL6::INSTR")
except:
    print("Keithley not found on port ASRL6::INSTR")
    print("Trying ASRL5::INSTR")
    sourcemeter = Keithley2400("ASRL5::INSTR")
#print(sourcemeter.id)

if is_source_current is True:
    if is_source_voltage is True:
        print("Both is_source_current and is_source_voltage is set to True")
        print("Defaulting to source_current")
    sourcemeter.apply_current()
    sourcemeter.compliance_voltage = voltage_limit
    sourcemeter.source_current = source_current
elif is_source_voltage is True:
    sourcemeter.apply_voltage()
    sourcemeter.compliance_current = current_limit
    sourcemeter.source_voltage = source_voltage

print("Expt start time: " + asctime())
start_time = time()

print("Turning on source {}".format("current" if is_source_current is True else "voltage"))
print("Source: {}".format(str(source_current) + " A" if is_source_current is True else str(source_voltage) + " V" ))
print("Limit: {}".format(str(voltage_limit) + " V" if is_source_current is True else str(current_limit) + " A" ))
print("")
sourcemeter.enable_source()

try:
    while 1:

        # Exit time delay and increase time counter
        time_counter = time_counter + 1
        
        # measure voltage
        sourcemeter.measure_voltage()
        voltages.append(sourcemeter.voltage)
        
        # measure current
        sourcemeter.measure_current()
        currents.append(sourcemeter.current)

        # get the current time
        times.append(asctime())
        
        # print out current time and measurements
        print(str(times[-1]) + ": " + str(voltages[-1]) + " | " + str(currents[-1]) )
        
        if(len(voltages) >= no_of_points_per_file * save_count):
            data = pd.DataFrame({
                'Voltage (V)': voltages,
                'Current (A)': currents,
                'Time': times
            })
            
            data.to_csv(csv_name + str(file_count) + '.csv')
            print("\nFile save: " + csv_name + str(file_count) + '.csv\n')
            file_count = file_count + 1
            save_count = save_count + 1
        
        # Stop loop if max no of data points is reached
        if(counter > data_points):
            break
        
        # Increment only if data_point is defined i.e not 0
        if(data_points > 0):
            counter = counter + 1
            
        end_time = start_time + time_delay * time_counter
        while(end_time > time()):
            sleep(1)
except:
    pass

# Save the data columns in a CSV file
data = pd.DataFrame({
    'Voltage (V)': voltages,
    'Current (A)': currents,
    'Time': times
})

data.to_csv(csv_name + str(file_count) + '.csv')
print("\nFile save: " + csv_name + str(file_count) + '.csv')
print("\nExpt start time: " + asctime(localtime(start_time)))
print("Expt stop time: " + asctime())
print("Number of data points: " + str(time_counter-1))

sourcemeter.shutdown()
 