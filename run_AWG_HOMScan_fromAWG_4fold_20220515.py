"""
AWG code for HOM measurements.

AWG70k Simple Waveform Sender
Creates waveforms + markers for Channel 1 (one pulse) and Channel 2 (one pulse),
sends them to the AWG, and loads them onto the respective channels.

Edited: 07/27/21
Sam Davis

Requirements: Python3, AWGFunc.py (in same directory), packages listed below
OS: CentOS 7
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import AWGFunc
import time
from datetime import datetime

sampleRate = AWGFunc.awg_sampleRate
Vmin = AWGFunc.awg_Vmin
Vmax = AWGFunc.awg_Vmax
repRate = 10e6 #Clock rate (Hz)
#repRate = 80*10**6 #Clock rate (Hz)
clockCycle = 1/repRate
wfmPulseWidth= 3*40e-12 #in seconds
markerPulseWidth =10*40e-12
#markerPulseWidth = 6000e-12
adqtime= np.array([5,5,5,5,5,5,5,5,5,5,5,5,5,5,5])*1#seconds
#pulse center changed  Bob .5--> .1 and Alice .74--> .1


delayStep = 40*10**(-12) #s
scanRange = 1800 * 10**(-12)
delayStepFrac = delayStep/clockCycle

numSteps =round(scanRange/delayStep)
#numSteps=14

print("numSteps: ",numSteps)

pulseSep = 10 *10**(-9)
#numSteps = 0

#Alice Pos
pulseCenterWfm_Ch1 = 0.18
#Alice Marker
pulseCenterMkr1_Ch1 = 0.2# 07
#Bob Pos
pulseCenterWfm_Ch2 = 0.1537+24*delayStepFrac#0.15#0.083 changed from 22 --> 26 --> 34
print(0.1537+7*delayStepFrac)
#pulseCenterWfm_Ch2 = pulseCenterWfm_Ch2-11*delayStepFrac+11*delayStepFrac
#Bob Marker
pulseCenterMkr1_Ch2 = 0.15

print((pulseCenterWfm_Ch2-pulseCenterWfm_Ch1)*2500*40)


try:


    # Set up VISA instrument object
    rm = visa.ResourceManager('@py')
    awg = rm.open_resource('TCPIP0::192.168.2.111::inst0::INSTR')
    print('Connected to ', awg.query('*idn?'))


    # Create Waveform for Channel 1
    name_ch1 = 'HOM_wfm_CH1'
    wfm_arr_ch1=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth, pulseCenter = pulseCenterWfm_Ch1) #Creates single pulse for channel 1
    #wfm_arr_ch1=AWGFunc.createWaveformTwoPulseArray(repRate, wfmPulseWidth,pulseSep,pulseCenter=pulseCenterWfm_Ch1) #Creates double pulse for channel 1
    numSamples_ch1 = len(wfm_arr_ch1)


    # Create Marker Data for Channel 1
    marker2_arr_ch1 = AWGFunc.createMarkerZerosArray(repRate)
    marker1_arr_ch1 = AWGFunc.createMarkerOnePulseArray(repRate,markerPulseWidth, pulseCenter = pulseCenterMkr1_Ch1) #Instead of one-sided step fxn, use pulse
    markerData_ch1=AWGFunc.createMarkerData(marker1_arr_ch1,marker2_arr_ch1)

    #Send Waveform + Markers to Channel 1
    AWGFunc.sendWaveform(awg, name_ch1, numSamples_ch1, wfm_arr_ch1)
    AWGFunc.sendMarkerData(awg, name_ch1, numSamples_ch1, markerData_ch1)


    #Load Waveform + Markers onto Channel 1
    AWGFunc.loadWaveform(awg, name_ch1, 1)







    #Create Waveform for Channel 2
    name_ch2 = 'HOM_wfm_CH2'
    wfm_arr_ch2=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth, pulseCenter=pulseCenterWfm_Ch2) #Creates single pulse for channel 2
    #wfm_arr_ch2=AWGFunc.createWaveformTwoPulseArray(repRate, wfmPulseWidth,pulseSep,pulseCenter=pulseCenterWfm_Ch2) #Creates double pulse for channel 2
    numSamples_ch2 = len(wfm_arr_ch2)


    # Create Marker Data for Channel 2
    marker1_arr_ch2 = AWGFunc.createMarkerOnePulseArray(repRate,markerPulseWidth, pulseCenter = pulseCenterMkr1_Ch2) #Instead of one-sided step fxn, use pulse

    marker2_arr_ch2 = AWGFunc.createMarkerZerosArray(repRate)
    markerData_ch2=AWGFunc.createMarkerData(marker1_arr_ch2,marker2_arr_ch2)

    #Send Waveform + Markers to Channel 2
    AWGFunc.sendWaveform(awg, name_ch2, numSamples_ch2, wfm_arr_ch2)
    AWGFunc.sendMarkerData(awg, name_ch2, numSamples_ch2, markerData_ch2)


    #Load Waveform + Markers onto Channel 2
    AWGFunc.loadWaveform(awg, name_ch2, 2)





    # Check for errors
    AWGFunc.checkErrors(awg)

    #Turn on outputs
    awg.write('output1 on')
    awg.write('output2 on')
    awg.write('awgcontrol:run:immediate')
    print(adqtime[0])

    time.sleep(adqtime[0])

    steps = [6,10,2,2,1,1,1,1,1,1,2,2,10,6]

    for j,i in enumerate(steps):
        print ("Step number: ",j+1)
        print ("Step size: ",i*40,"(ps)")
        # if  i < 2:
        #     continue
        pulseCenterWfm_Ch2 = pulseCenterWfm_Ch2-i*delayStepFrac

        #pulseCenterWfm_Ch2 = pulseCenterWfm_Ch2-sum(steps[0:7])*delayStepFrac

        print(pulseCenterWfm_Ch2)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
        wfm_arr_ch2=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth, pulseCenter=pulseCenterWfm_Ch2) #Creates single pulse for channel 2
        #wfm_arr_ch2=AWGFunc.createWaveformTwoPulseArray(repRate, wfmPulseWidth,pulseSep,pulseCenter=pulseCenterWfm_Ch2) #Creates double pulse for channel 2
        numSamples_ch2 = len(wfm_arr_ch2)


        # Create Marker Data for Channel 2
        marker1_arr_ch2 = AWGFunc.createMarkerOnePulseArray(repRate,markerPulseWidth,pulseCenter=pulseCenterMkr1_Ch2) #Instead of one-sided step fxn, use pulse
        marker2_arr_ch2 = AWGFunc.createMarkerZerosArray(repRate)
        markerData_ch2=AWGFunc.createMarkerData(marker1_arr_ch2,marker2_arr_ch2)

        #Send Waveform + Markers to Channel 2
        AWGFunc.sendWaveform(awg, name_ch2, numSamples_ch2, wfm_arr_ch2)
        AWGFunc.sendMarkerData(awg, name_ch2, numSamples_ch2, markerData_ch2)


        #Load Waveform + Markers onto Channel 2
        AWGFunc.loadWaveform(awg, name_ch2, 2)

        awg.write('awgcontrol:run:immediate')


        AWGFunc.checkErrors(awg)
        #pulseCenterWfm_Ch2 = pulseCenterWfm_Ch2-delayStepFrac
        print(adqtime[j+1])
        time.sleep(adqtime[j+1])

    awg.close()
except KeyboardInterrupt:
    awg.close()
