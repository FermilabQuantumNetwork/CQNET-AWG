"""
AWG70k Simple Waveform Sender
Creates waveform, sends it to the AWG, assigns
it to Ch1 and plays it out.

CentOS 7
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import AWGFunc

sampleRate = AWGFunc.awg_sampleRate
Vmin = AWGFunc.awg_Vmin
Vmax = AWGFunc.awg_Vmax


# Set up VISA instrument object
rm = visa.ResourceManager('@py')
awg = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')
print('Connected to ', awg.query('*idn?'))

# Create Waveform
name1 = '2pulseDec18_wfm_CH1'
name2 = '2pulseDec18_wfm_CH2'
repRate = 100*10**6#1/(7*10**(-9))#100e6
pulseWidth=40e-12
pulseSep=2e-9
wfm_arr1=AWGFunc.createWaveformTwoPulseArray(repRate, pulseWidth, pulseSep)
wfm_arr2=AWGFunc.createWaveformOnePulseArray(repRate, pulseWidth, pulseCenter=0.87)
numSamples = len(wfm_arr1)
sample_arr = range(numSamples)
time_arr = []
for s in sample_arr:
    time_arr.append(s*10**9 / sampleRate)
time_arr=np.array(time_arr)

# Create Marker Data
marker1_arr = -AWGFunc.createWaveformOnePulseArray(repRate,400e-12)#createMarker1Array(repRate)
marker2_arr = AWGFunc.createMarker2Array(repRate)
markerData=AWGFunc.createMarkerData(marker1_arr,marker2_arr)






# Send Waveform Data
AWGFunc.sendWaveform(awg, name1, numSamples, wfm_arr1)
#Send Marker data
AWGFunc.sendMarkerData(awg, name1, numSamples, markerData)

# Send Waveform Data
AWGFunc.sendWaveform(awg, name2, numSamples, wfm_arr2)
#Send Marker data
AWGFunc.sendMarkerData(awg, name2, numSamples, markerData)

# Load waveform, being playback, and turn on output
#channelNum = 2
AWGFunc.loadWaveform(awg, name1, 1)
AWGFunc.loadWaveform(awg, name2, 2)
#AWGFunc.loadWaveform(awg, "alex_wfm", 2)


awg.write('output1 on')
awg.write('output2 off')
#awg.write('awgcontrol:run:immediate')

# Check for errors
AWGFunc.checkErrors(awg)

awg.close()
