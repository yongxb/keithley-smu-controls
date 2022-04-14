# Keithley SMU Control

 
## What this does
This contains codes to connect, control and log the output of Keithley SMU devices using python. It contains codes for the following modes and devices

### Modes
Constant source current
Constant source voltage

### Devices
Keithley 2400
Keithley 2450
Keithley 2657A

## Requirement
### Python packages
|Package                        |Purpose                                       |
|-------------------------------|----------------------------------------------|
|PyVISA                         | Connection to Keithley 2450, 2657A           |
|PyMeasure                      | Connection to Keithley 2400                  |
|Pandas                         | Data logging of sourced current/voltage      |

### Connection to device
The VIAS resource name which the device is connected to needs to be specified. This can be obtained from LABVIEW. Alternatively, they can be found by running the following codes (if PyVISA is installed)
```
import pyvisa
rm = pyvisa.ResourceManager()
rm.list_resources()
```

|Connected via            |Examples                                |
|-------------------------|----------------------------------------|
|Serial port RS232        | ASRL1::INSTR                           |
|USB                      | USB0::0x05E6::0x2450::04373013::INSTR  |
|Ethernet port            | TCPIP0::169.254.0.1::inst0::INSTR      |
