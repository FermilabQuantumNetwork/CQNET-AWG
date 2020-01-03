"""

AWG70k Simple Waveform Sender
Creates a two pulse waveform, plots, the waveform,
sends it to the AWG, assigns it to Ch2 and plays it out.

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
name = 'sam1_wfm'
repRate = 100e6 #clock rate (Hz)
pulseWidth=40e-12 #in seconds
pulseSep=2e-9 #in seconds
wfm_arr=AWGFunc.createWaveformTwoPulseArray(repRate, pulseWidth, pulseSep) #Creates normalized voltage array of two pulses
numSamples = len(wfm_arr)
sample_arr = range(numSamples) #array of sample indices
time_arr = []
for s in sample_arr:
    time_arr.append(s*10**9 / sampleRate)
time_arr=np.array(time_arr)

# Create Marker Data
marker1_arr = AWGFunc.createMarkerStepArray(repRate)
marker2_arr = AWGFunc.createMarkerZerosArray(repRate)
markerData=AWGFunc.createMarkerData(marker1_arr,marker2_arr)


#Plot waveform + markers before sending to AWG
#Stacked plot of all data
fig, axs = plt.subplots(3,1, num=1, sharex=True)
#WaveForm
axs[0].plot(time_arr, wfm_arr,".")
axs[0].set_ylabel("Waveform (Norm. V)")
axs[0].grid()
#Marker 1
axs[1].plot(time_arr, marker1_arr)
axs[1].set_ylabel("Marker 1 (Bits)")
axs[1].grid()
#Marker 2
axs[2].plot(time_arr, marker2_arr)
axs[2].set_ylabel("Marker 2 (Bits)")
axs[2].grid()
xlims=axs[2].get_xlim()
xmin1=xlims[0]
xmax1=xlims[1]
fig.suptitle("Waveform and Markers for One Clock Cycle")
plt.xlabel('Time (ns)', fontsize =16)
plt.show()


# Send Waveform Data
AWGFunc.sendWaveform(awg, name, numSamples, wfm_arr)
#Send Marker data
AWGFunc.sendMarkerData(awg, name, numSamples, markerData)

# Load waveform onto channel 2, turn on output, and begin playback
channelNum = 2
AWGFunc.loadWaveform(awg, name, channelNum)

#IMPORTANT: If not sending anything to a channel, need to write the corresponding output off.
awg.write('output1 off')
awg.write('output2 on')
awg.write('awgcontrol:run:immediate') #Start run

# Check for errors
AWGFunc.checkErrors(awg)

awg.close()
