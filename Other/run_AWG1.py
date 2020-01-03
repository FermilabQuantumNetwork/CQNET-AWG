import matplotlib.pyplot as plt
import numpy as np
import pathlib
import pyvisa as visa
import qcodes.instrument_drivers.tektronix.AWG70002A
from qcodes.instrument_drivers.tektronix.AWG70002A import AWG70002A
awg = AWG70002A('awg', 'TCPIP0::192.168.0.165::inst0::INSTR')

#rm = visa.ResourceManager('@py')
#awg1 = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')


#Check available parameters
awg.print_readable_snapshot(update=True)


# set the instrument in awg mode
awg.mode('AWG')
# set the resolution to 8 bits plus two markers
awg.ch1.resolution(8)

# clear the sequence list and waveform list (NOT ALWAYS A GOOD IDEA! BE CAREFUL!)
awg.clearSequenceList()
awg.clearWaveformList()

# Let us make a sine, upload it and play it
N = 2400  # minimal length allowed is 2400 points

m1 = np.concatenate((np.ones(int(N/2)), np.zeros(int(N/2))))
m2 = np.concatenate((np.zeros(int(N/2)), np.ones(int(N/2))))

ramp = 0.075*np.linspace(0, 1, N)

mysine = 0.1*np.sin(10*2*np.pi*np.linspace(0, 1, N)) + ramp

data = np.array([mysine, m1, m2])
print(data)
dataBinary = data.astype(np.float32).tostring()
#print(dataBinary)
# The .wfmx file needs a name in the memory of the instrument
# The name of the waveform in the waveform list is that same name
# with no .wfmx extension
filename = 'examplewaveform1.wfmx'#r'C:\Users\OEM\Documents\Raju\examplewaveform1.wfmx'
name="examplewaveform1"
wfmx_file=awg.makeWFMXFile(data,0.350)
# now compile the binary file
#awg1.write('wlist:waveform:new "{}", {}'.format(name, len(mysine)))
#print(wfmx_file)
#stringArg = 'wlist:waveform:marker:data "{}", 0, {}, '.format(name, len(data))
# awg1.write(stringArg)
# stringArg = 'wlist:waveform:marker:data "{}", 0, {}, '.format(name, len(mysine))
# awg1.write_binary_values(stringArg, wfmx_file)


# and send it and load it into memory
awg.sendWFMXFile(wfmx_file,filename)
awg.loadWFMXFile(filename)

# The waveform is now in the waveform list
#print(awg.waveformList)

# now assign it to channel 1
#awg.ch1.setWaveform(filename.replace('.wfmx', ''))

#error = awg1.query('system:error:all?')
#print('Status: {}'.format(error))
