"""
AWG code for HOM measurements.

AWG70k Simple Waveform Sender
Creates waveforms + markers for Channel 1 (one pulse) and Channel 2 (one pulse),
sends them to the AWG, and loads them onto the respective channels.

Edited: 1/3/20
Sam Davis

Requirements: Python3, AWGFunc.py (in same directory), packages listed below
OS: CentOS 7
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import AWGFunc

sampleRate = AWGFunc.awg_sampleRate
Vmin = AWGFunc.awg_Vmin
Vmax = AWGFunc.awg_Vmax
repRate = 100*10**6 #Clock rate (Hz)
wfmPulseWidth=40e-12 #in seconds
markerPulseWidth = 400e-12

# Set up VISA instrument object
rm = visa.ResourceManager('@py')
awg = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')
print('Connected to ', awg.query('*idn?'))


# Create Waveform for Channel 1
name_ch1 = 'HOM_wfm_CH1'
wfm_arr_ch1=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth) #Creates single pulse for channel 1
numSamples_ch1 = len(wfm_arr_ch1)

#Create Waveform for Channel 2
name_ch2 = 'HOM_wfm_CH2'
wfm_arr_ch2=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth, pulseCenter=0.87) #Creates single pulse for channel 2
numSamples_ch2 = len(wfm_arr_ch2)


# Create Marker Data for Channel 1
marker1_arr_ch1 = -AWGFunc.createMarkerOnePulseArray(repRate,markerPulseWidth) #Instead of one-sided step fxn, use pulse
marker2_arr_ch1 = AWGFunc.createMarkerZerosArray(repRate)
markerData_ch1=AWGFunc.createMarkerData(marker1_arr_ch1,marker2_arr_ch1)


# Create Marker Data for Channel 2
marker1_arr_ch2 = -AWGFunc.createMarkerOnePulseArray(repRate,markerPulseWidth) #Instead of one-sided step fxn, use pulse
marker2_arr_ch2 = AWGFunc.createMarkerZerosArray(repRate)
markerData_ch2=AWGFunc.createMarkerData(marker1_arr_ch2,marker2_arr_ch2)

#Send Waveform + Markers to Channel 1
AWGFunc.sendWaveform(awg, name_ch1, numSamples_ch1, wfm_arr_ch1)
AWGFunc.sendMarkerData(awg, name_ch1, numSamples_ch1, markerData_ch1)

#Send Waveform + Markers to Channel 2
AWGFunc.sendWaveform(awg, name_ch2, numSamples_ch2, wfm_arr_ch2)
AWGFunc.sendMarkerData(awg, name_ch2, numSamples_ch2, markerData_ch2)

#Load Waveform + Markers onto Channel 1
AWGFunc.loadWaveform(awg, name_ch1, 1)

#Load Waveform + Markers onto Channel 2
AWGFunc.loadWaveform(awg, name_ch2, 2)

#Turn on outputs
awg.write('output1 on')
awg.write('output2 on')
#awg.write('awgcontrol:run:immediate')

# Check for errors
AWGFunc.checkErrors(awg)

awg.close()
