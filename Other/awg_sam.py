# Sam's working code for controlling the AWG
"""
AWG70k Simple Waveform Sender
Creates a simple sine wave, sends it to the AWG, assigns
it to Ch1 and plays it out.

Edited: Nov 11, 2019
Alex Walter

CentOS 7
Python 3.6.8 64-bit
NumPy 1.17.3, PyVISA 1.8
"""

import pyvisa as visa
import numpy as np

#print('NumPy Version:', np.__version__)
#print('PyVISA Version:', visa.__version__)

# Set up VISA instrument object
rm = visa.ResourceManager('@py')
awg = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')
print('Connected to ', awg.query('*idn?'))
#awg.write('*rst')
#awg.write('*cls')


# Create Waveform
name = 'sam_wfm'
sampleRate = 25e9
recordLength = 2400
freq = 100e6
t = np.linspace(0, recordLength/sampleRate, recordLength)#, dtype=np.float32)
wfmData = np.sin(2*np.pi*freq*t)

# Create Marker Data
# Marker data is an 8 bit value. Bit 6 is marker 1 and bit 7 is marker 2
#exData1 = (1 << 6) * np.random.randint(2, size=recordLength, dtype=np.uint8)
#exData2 = (1 << 7) * np.random.randint(2, size=recordLength, dtype=np.uint8)
marker1_arr = np.random.randint(2, size=recordLength, dtype=np.uint8)
marker2_arr = np.random.randint(2, size=recordLength, dtype=np.uint8)
exData1 = (1 << 6) * marker1_arr.astype(np.uint8)#, size=recordLength, dtype=np.uint8)
exData2 = (1 << 7) * marker2_arr.astype(np.uint8)#, size=recordLength, dtype=np.uint8)

markerData = exData1 + exData2



# Send Waveform Data
delete_wfm = 'wlist:waveform:delete "{:s}"'.format(name)
create_wfm = 'wlist:waveform:new "{:s}", {:d}'.format(name, recordLength)
wfm_bytes = len(wfmData) * 4
wfm_header = 'wlist:waveform:data "{:s}", 0, {:d}, '.format(name, recordLength, len(str(wfm_bytes)), wfm_bytes)

awg.write(delete_wfm)
awg.write(create_wfm)
ret=awg.write_binary_values(wfm_header, wfmData)
print('Waveform bytes: {}'.format(ret))

#Send Marker data
marker_bytes = len(markerData)
marker_header = 'wlist:waveform:marker:data "{:s}", 0, {:d}, '.format(name, recordLength, len(str(wfm_bytes)), wfm_bytes)
ret=awg.write_binary_values(marker_header, markerData,datatype='B')
print('Waveform bytes: {}'.format(ret))


# Load waveform, being playback, and turn on output
awg.write('source1:waveform "{}"'.format(name))
#awg.write('awgcontrol:run:immediate')
#awg.query('*opc')
#awg.write('output1 on')

# Check for errors
error = awg.query('system:error:all?')
print('Status: {}'.format(error))

awg.close()
