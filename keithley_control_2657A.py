import visa
from time import sleep, asctime, localtime, time
import pandas as pd

#### Input parameters
data_points = 100
no_of_points_per_file = 30

time_delay = 1 # in seconds

is_source_current = False
source_current = 200e-6 # in A
voltage_limit = 200 # in V

is_source_voltage = True
source_voltage = 3000 # in V
current_limit = 0.001 # in A

soak_time = 10 # in seconds

#### Save file location/name
csv_name = '23April2019_' ## Need to change

#### Initialize list ####
current_list = []
voltage_list = []
time_list = []

#### Counters ####
counter = 0
file_count = 0
time_counter = 0
save_count = 1

### Connect to keithley
rm = visa.ResourceManager()
#print(rm.list_resources())
keithley = rm.open_resource('TCPIP0::169.254.0.1::inst0::INSTR')
print("Using " + keithley.query('*IDN?'))
sleep(1) # to ensure that the above prints properly

#Initialize SMU
keithley.write(" \
reset() \n\
errorqueue.clear() \n\
status.reset() \
")

if is_source_current is True:
    if is_source_voltage is True:
        print("Both is_source_current and is_source_voltage is set to True")
        print("Defaulting to source_current")
    #Configure source/measure functions
    keithley.write(" \
    smua.source.func = smua.OUTPUT_DCAMPS \n\
    smua.source.leveli = {levelI} \n\
    display.smua.measure.func = display.MEASURE_DCVOLTS \n\
    smua.measure.autozero = smua.AUTOZERO_ONCE \n\
    smua.measure.autorangev = smua.AUTORANGE_ON \n\
    smua.source.limitv = {limitV} \
    ".format(levelI = source_current, limitV = voltage_limit))

elif is_source_voltage is True:
    #Configure source/measure functions
    keithley.write(" \
    smua.source.func = smua.OUTPUT_DCVOLTS \n\
    smua.source.levelv = {levelV} \n\
    display.smua.measure.func = display.MEASURE_DCAMPS \n\
    smua.measure.autozero = smua.AUTOZERO_ONCE \n\
    smua.measure.autorangei = smua.AUTORANGE_ON \n\
    smua.source.limiti = {limitI} \
    ".format(levelV = source_voltage, limitI = current_limit))

print("Expt start time: " + asctime())
start_time = time()

#Turn on output
print("Turning on source {}".format("current" if is_source_current is True else "voltage"))
print("Source: {}".format(str(source_current) + " A" if is_source_current is True else str(source_voltage) + " V" ))
print("Limit: {}".format(str(voltage_limit) + " V" if is_source_current is True else str(current_limit) + " A" ))
print("")
keithley.write("smua.source.output = 1")

try:
    while 1:
        # Check if interlock is still enabled
        keithley.write("counter = errorqueue.count")
        error_count = keithley.query("print(counter)")[:-2]
        if float(error_count) > 0:
            keithley.write("errorId = errorqueue.next()")
            error_id = keithley.query("print(errorId)")[:-2]
            if float(error_id) == 8.02:
                raise AssertionError()
            print("Error occured: " + str(error_id))
            break

        # Increase time counter
        time_counter = time_counter + 1

        # Stop loop if max no of data points is reached
        if(counter > data_points):
            break

        # Increment only if data_point is defined i.e not 0
        if(data_points > 0):
            counter = counter + 1

        #Take measurements
        keithley.write("ireading, vreading = smua.measure.iv(smua.nvbuffer1, smua.nvbuffer2)")
        current = keithley.query("print(ireading)")[:-2] # to remove \n string at end
        voltage = keithley.query("print(vreading)")[:-2]

        current_list.append(current)
        voltage_list.append(voltage)
        time_list.append(asctime())
        # print out current time and measurements
        print(str(time_list[-1]) + ": " + str(voltage_list[-1]) + " | " + str(current_list[-1]))

        if(len(time_list) >= no_of_points_per_file * save_count):
            data = pd.DataFrame({
                'Voltage (V)': voltage_list,
                'Current (A)': current_list,
                'Time': time_list
            })

            data.to_csv(csv_name + str(file_count) + '.csv')
            print("\nFile save: " + csv_name + str(file_count) + '.csv\n')
            file_count = file_count + 1
            save_count = save_count + 1

        # Delay next measurement
        end_time = start_time + time_delay * time_counter
        while(end_time > time()):
            sleep(0.5)

except AssertionError:
    print("\n----------------------------")
    print("Output blocked by interlock!")
    print("----------------------------")
except:
    pass

# Save the data columns in a CSV file
data = pd.DataFrame({
    'Voltage (V)': voltage_list,
    'Current (A)': current_list,
    'Time': time_list
})

data.to_csv(csv_name + str(file_count) + '.csv')
print("\nFile save: " + csv_name + str(file_count) + '.csv')
print("\nExpt start time: " + asctime(localtime(start_time)))
print("Expt stop time: " + asctime())
print("Number of data points: " + str(time_counter-1))

#Turn off output and drain capacitors
if is_source_current is True:
    print("\nSetting source current to 0 A")
    keithley.write("smua.source.leveli = 0")
if is_source_voltage is True:
    print("\nSetting source voltage to 0 V")
    keithley.write("smua.source.levelv = 0")

print("Wait {}s until capacitors are fully discharged".format(soak_time))
sleep(soak_time)

print("Turning off output")
keithley.write("smua.source.output = 0")

print("Closing Keithley connection")
keithley.close()