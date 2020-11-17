import visa
from time import sleep, asctime, localtime, time
import pandas as pd

#### Input parameters
data_points = 0
no_of_points_per_file = 30

time_delay = 120 # in seconds

is_source_current = True
source_current = -50e-6 # in A
voltage_limit = 210 # in V

is_source_voltage = False
source_voltage = 200 # in V
current_limit = 1e-4 # in A

soak_time = 10 # in seconds
buffer_size = 1e6

#### Save file location/name
csv_name = '10Dec2019_' ## Need to change

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
keithley_port = [port for port in rm.list_resources() if 'USB' in port]
keithley = rm.open_resource(keithley_port[0]) # assumes Keithley 2450 is the only VISA device attached to the usb ports
print("Using " + keithley.query('*IDN?'))
sleep(1) # to ensure that the above prints properly

#Initialize SMU
keithley.write(" \
reset() \n\
eventlog.clear() \n\
status.reset() \
")

if is_source_current is True:
    if is_source_voltage is True:
        print("Both is_source_current and is_source_voltage is set to True")
        print("Defaulting to source_current")
    #Configure source/measure functions
    keithley.write(" \
    smu.source.func = smu.FUNC_DC_CURRENT \n\
    smu.source.level = {levelI} \n\
    smu.measure.autozero.once() \n\
    smu.measure.autorange = smu.ON \n\
    smu.source.vlimit.level = {limitV} \n\
    smu.source.readback = smu.ON \
    ".format(levelI = source_current, limitV = voltage_limit))

elif is_source_voltage is True:
    #Configure source/measure functions
    keithley.write(" \
    smu.source.func = smu.FUNC_DC_VOLTAGE \n\
    smu.source.level = {levelV} \n\
    smu.measure.autozero.once() \n\
    smu.measure.autorange = smu.ON \n\
    smu.source.ilimit.level = {limitI} \n\
    smu.source.readback = smu.ON \
    ".format(levelV = source_voltage, limitI = current_limit))

print("Expt start time: " + asctime())
start_time = time()

#Initialize buffers
keithley.write("sourceBuffer = buffer.make({})".format(buffer_size))

#Turn on output
print("Turning on source {}".format("current" if is_source_current is True else "voltage"))
print("Source: {}".format(str(source_current) + " A" if is_source_current is True else str(source_voltage) + " V" ))
print("Limit: {}".format(str(voltage_limit) + " V" if is_source_current is True else str(current_limit) + " A" ))
print("")
keithley.write("smu.source.output = smu.ON")

try:
    while 1:
        # Check if error has occured enabled
        keithley.write("counter = eventlog.getcount(eventlog.SEV_ERROR)")
        error_count = keithley.query("print(counter)")
        if float(error_count) > 0:
            keithley.write("errorId = eventlog.next()")
            error_id = keithley.query("print(errorId)")
            print("\n----------------------------")
            print("Error occured: " + str(error_id))
            print("----------------------------")
            break

        # Check if user has turned off output
        output = keithley.query("print(smu.source.output)")[:-1]
        if output == "smu.OFF":
            print("\n----------------------------")
            print("User has turned off output")
            print("----------------------------")
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
        if is_source_current is True:
            keithley.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
            keithley.write("vreading = smu.measure.read(sourceBuffer)")
            voltage = keithley.query("print(vreading)")[:-1]
            current = keithley.query("print(sourceBuffer.sourcevalues[sourceBuffer.n])")[:-1]
        if is_source_voltage is True:
            keithley.write("smu.measure.func = smu.FUNC_DC_CURRENT")
            keithley.write("ireading = smu.measure.read(sourceBuffer)")
            current = keithley.query("print(ireading)")[:-1] # to remove \n string at end
            voltage = keithley.query("print(sourceBuffer.sourcevalues[sourceBuffer.n])")[:-1]

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
    keithley.write("smu.source.level = 0")
if is_source_voltage is True:
    print("\nSetting source voltage to 0 V")
    keithley.write("smu.source.level = 0")

print("Wait {}s until capacitors are fully discharged".format(soak_time))
sleep(soak_time)

print("Turning off output")
keithley.write("smu.source.output = smu.OFF")

print("Closing Keithley connection")
keithley.close()