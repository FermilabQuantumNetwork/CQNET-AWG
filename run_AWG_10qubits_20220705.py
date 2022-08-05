"""

AWG70k Simple Waveform Sender
Creates a two pulse waveform, plots, the waveform,
sends it to the AWG, assigns it to Ch2 and plays it out.

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


# Set up VISA instrument object
rm = visa.ResourceManager('@py')
awg = rm.open_resource('TCPIP0::192.168.2.111::inst0::INSTR')
print('Connected to ', awg.query('*idn?'))

# Create Waveform
name       = 'sam1_wfm'
name2       = 'sam2_wfm'
repRate    = 10e6 #clock rate (Hz)
clockCycle = 1/repRate
print(clockCycle)
pulseN     = 10 #number of pulses
pulseWidth = 2*40e-12 #in seconds
pulseSep   = 4.2e-9 #in seconds
separation = 2.1e-9/clockCycle
pulseStart = 0.025 #fraction of sample in which pulse will start Starting point of pulses
pulseStart_2 = 0.025-separation #fraction of sample in which pulse will start Starting point of pulses
diff = 0.012
wfm_arr  = AWGFunc.createWaveformNPulseArray(repRate, pulseN, pulseWidth, pulseSep, pulseStart=pulseStart+diff) #Creates normalized voltage array of two pulses
wfm_arr_2= AWGFunc.createWaveformNPulseArray(repRate, pulseN, pulseWidth, pulseSep, pulseStart=pulseStart_2+diff) #Creates normalized voltage array of two pulses
wfm_arr = wfm_arr + wfm_arr_2
wfm_arr_3  = AWGFunc.createWaveformNPulseArray(repRate, pulseN, pulseWidth, pulseSep, pulseStart=pulseStart) #Creates normalized voltage array of two pulses
wfm_arr_4 = AWGFunc.createWaveformNPulseArray(repRate, pulseN, pulseWidth, pulseSep, pulseStart=pulseStart_2) #Creates normalized voltage array of two pulses
wfm_arr_3 = wfm_arr_3+wfm_arr_4
numSamples = len(wfm_arr)
sample_arr = range(numSamples) #array of sample indices
time_arr = []
for s in sample_arr:
    time_arr.append(s*10**9 / sampleRate)
time_arr=np.array(time_arr)

plt.plot(wfm_arr)
plt.show()

# Create Marker Data
markerWidth = 10*40e-12 #in seconds
markerStart = 0.99 #Starting point of marker
marker1_arr = AWGFunc.createMarkerOnePulseArray(repRate, markerWidth, pulseStart=markerStart)
marker2_arr = AWGFunc.createMarkerZerosArray(repRate)
markerData  = AWGFunc.createMarkerData(marker1_arr,marker2_arr)


#Plot waveform + markers before sending to AWG
#Stacked plot of all data
fig, axs = plt.subplots(3,1, num=1, sharex=True)
#WaveForm
axs[0].plot(time_arr, wfm_arr,".")
axs[0].set_ylabel("Waveform (Norm. V)")
axs[0].grid()
##Marker 1
#axs[1].plot(time_arr, marker1_arr)
#axs[1].set_ylabel("Marker 1 (Bits)")
#axs[1].grid()
#Marker 2
#axs[2].plot(time_arr, marker2_arr)
#axs[2].set_ylabel("Marker 2 (Bits)")
#axs[2].grid()
#xlims=axs[2].get_xlim()
#xmin1=xlims[0]
#xmax1=xlims[1]
#fig.suptitle("Waveform and Markers for One Clock Cycle")
#plt.xlabel('Time (ns)', fontsize =16)
#\plt.show()


# Send Waveform Data
AWGFunc.sendWaveform(awg, name, numSamples, wfm_arr)
AWGFunc.sendWaveform(awg, name2, numSamples, wfm_arr_3)
#Send Marker data
AWGFunc.sendMarkerData(awg, name, numSamples, markerData)

# Load waveform onto channel 2, turn on output, and begin playback
channelNum = 1
AWGFunc.loadWaveform(awg, name, channelNum)

#AWGFunc.sendWaveform(awg, name, numSamples, wfm_arr_2)
AWGFunc.loadWaveform(awg, name2, 2)

#IMPORTANT: If not sending anything to a channel, need to write the corresponding output off.
awg.write('output1 on')
awg.write('output2 on')
awg.write('awgcontrol:run:immediate') #Start run

# Check for errors
AWGFunc.checkErrors(awg)
