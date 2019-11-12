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
from AWGFunc import *


# Set up VISA instrument object
rm = visa.ResourceManager('@py')
awg = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')
print('Connected to ', awg.query('*idn?'))

# Create Waveform
name = 'sam_wfm'
sampleRate = 25e9
repRate = 2e6
recordLength = round(sampleRate/repRate)
print(recordLength)
freq = 100e6
t = np.linspace(0, recordLength/sampleRate, recordLength)#, dtype=np.float32)
wfmArr = 0.5*np.sin(2*np.pi*freq*t)

# Create Marker Data
marker1_arr = np.ones(recordLength)
marker2_arr = np.ones(recordLength)
markerData=createMarkerData(marker1_arr,marker2_arr)

# Send Waveform Data
sendWaveform(awg, name, recordLength, wfmArr)

#Send Marker data
sendMarkerData(awg, name, recordLength, markerData)

# Load waveform, being playback, and turn on output
loadWaveform(awg, name)
#awg.write('awgcontrol:run:immediate')
#awg.query('*opc')
#awg.write('output1 on')

# Check for errors
checkErrors(awg)

awg.close()
