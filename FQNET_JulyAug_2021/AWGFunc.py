"""
Functions for creating, sending, loading, and running waveforms/markers on the AWG.
This code is for a Tektronix AWG70002A.

Requirements: Python3, packages listed below
OS: CentOS 7
"""
import numpy as np
awg_sampleRate = 25e9 #in Hz
midway=0.5
awg_Vmin=-0.250 #in volts
awg_Vmax=0.250 #in volts

"""
Variables:
repRate = repetition rate (Hz)
pulseWidth = pulse width (seconds)
pulseCenter = start position of pulse in terms of fraction of clock cycle
Vmin = minimum voltage of waveform (volts)
Vmax = max voltage of waveforms (volts)
sampleRate = sample rate (Hz)
"""

#Creates an waveform with a single pulse.
def createWaveformOnePulseArray(repRate, pulseWidth, pulseCenter = midway, Vmin=awg_Vmin, Vmax=awg_Vmax, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate) #number of samples
    VminNorm=Vmin/awg_Vmax #normalized by amplitude
    VmaxNorm=Vmax/awg_Vmax #normalized by amplitude
    wfm_arr = VminNorm*np.ones(numSamples) #number of samples = length of normalized voltage array
    print("pulseWidthSampleSize: ", pulseWidth*sampleRate)
    pulseWidthSampleSize = round(pulseWidth*sampleRate) #number of samples in pulse
    pulseStartInd = round(numSamples*pulseCenter-pulseWidthSampleSize/2 - 1) #Make start index so center of pulse is at pulseCenter
    pulseEndInd = pulseStartInd + pulseWidthSampleSize #End index of pulse
    for i in range(pulseStartInd,pulseEndInd+1): #Make pulse
         wfm_arr[i] = VmaxNorm
    return wfm_arr #Return array of normalized voltages



#Creates an waveform with two pulses. #Here, the pulseCenter corresponds to midpoint of separation between pulses
def createWaveformTwoPulseArray(repRate,pulseWidth,pulseSep,pulseCenter=midway, Vmin=awg_Vmin, Vmax=awg_Vmax, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate) #number of samples
    VminNorm=Vmin/awg_Vmax #normalized by amplitude
    VmaxNorm=Vmax/awg_Vmax #normalized by amplitude
    wfm_arr = VminNorm*np.ones(numSamples) #number of samples = length of normalized voltage array
    print("pulseWidthSampleSize: ", pulseWidth*sampleRate)
    pulseWidthSampleSize = round(pulseWidth*sampleRate) #number of samples in a pulse
    pulseSepSampleSize = round(pulseSep*sampleRate) #number of samples separated pulses
    pulse1StartInd = round(numSamples*pulseCenter - pulseWidthSampleSize/2 - pulseSepSampleSize/2 - 1) #Start index of first pulse
    pulse1EndInd = pulse1StartInd + pulseWidthSampleSize #End index of first pulse
    for i in range(pulse1StartInd,pulse1EndInd): #Make pulse 1
        wfm_arr[i] = VmaxNorm
    pulse2StartInd = round(numSamples*pulseCenter - pulseWidthSampleSize/2 + pulseSepSampleSize/2 - 1) #Start index of second pulse
    pulse2EndInd = pulse2StartInd + pulseWidthSampleSize #End index of second pulse
    for i in range(pulse2StartInd,pulse2EndInd): #Make pulse two
        wfm_arr[i] = VmaxNorm
    return wfm_arr

#Creates step function array. onStart corresponds to the start of the step from min to max.
def createMarkerStepArray(repRate, onStart = midway, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate)
    marker_arr = np.zeros(numSamples)
    onStartInd = round(onStart*numSamples - 1)
    for i in range(onStartInd,numSamples):
        marker_arr[i] = 1
    return marker_arr

#Creates array of all zeros
def createMarkerZerosArray(repRate, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate)
    marker_arr = np.zeros(numSamples)
    return marker_arr


def createMarkerOnePulseArray(repRate, pulseWidth, pulseCenter = midway, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate) #number of samples
    marker_arr = np.zeros(numSamples)
    pulseWidthSampleSize = round(pulseWidth*sampleRate) #number of samples in pulse
    pulseStartInd = round(numSamples*pulseCenter-pulseWidthSampleSize/2 - 1) #Make start index so center of pulse is at pulseCenter
    pulseEndInd = pulseStartInd + pulseWidthSampleSize #End index of pulse
    for i in range(pulseStartInd,pulseEndInd+1): #Make pulse        
         marker_arr[i] = 1
    return marker_arr



#Creates the marker data to send to AWG
def createMarkerData(marker1_arr, marker2_arr):
    # Marker data is an 8 bit value. Bit 6 is marker 1 and bit 7 is marker 2
    exData1 = (1 << 6) * marker1_arr.astype(np.uint8)
    exData2 = (1 << 7) * marker2_arr.astype(np.uint8)
    markerData = exData1 + exData2
    return markerData


#Sends waveform to AWG
#Name = name of waveform, recordLength = num samples in waveform, wfmArr = array of normalized voltages (output of createWaveform...)
def sendWaveform(awg, name, recordLength, wfmArr):
    delete_wfm = 'wlist:waveform:delete "{:s}"'.format(name) #Command to delete waveform with same name from the waveform list
    create_wfm = 'wlist:waveform:new "{:s}", {:d}'.format(name, recordLength) #Command to create waveform with this name
    wfm_bytes = len(wfmArr) * 4 #Convert to number of bytes as specified by manual
    wfm_header = 'wlist:waveform:data "{:s}", 0, {:d}, '.format(name, recordLength, len(str(wfm_bytes)), wfm_bytes) #Wfm header (see manual)
    awg.write(delete_wfm)
    awg.write(create_wfm)
    ret=awg.write_binary_values(wfm_header, wfmArr) #Send waveform as binary values
    print('Waveform bytes: {}'.format(ret))
    return ret

#Send marker data to AWG
#Name = name of waveform, recordLength = num samples in marker (should be same as for wfm), markerData = in bits
def sendMarkerData(awg, name, recordLength, markerData):
    marker_bytes = len(markerData) * 4 #Convert to number of bytes as specified by manual
    marker_header = 'wlist:waveform:marker:data "{:s}", 0, {:d}, '.format(name, recordLength, len(str(marker_bytes)), marker_bytes) #Marker header (see manual)
    ret=awg.write_binary_values(marker_header, markerData,datatype='B') #Send marker data as binary values
    print('Marker bytes: {}'.format(ret))
    return ret


#Loads waveform + markers to AWG channel
def loadWaveform(awg, name, channelNum):
    if channelNum ==1:
        return awg.write('source1:waveform "{}"'.format(name))
    elif channelNum == 2:
        return awg.write('source2:waveform "{}"'.format(name))
    else:
        print("Enter valid channel number (1 or 2)")

#Checks for error reports from AWG
def checkErrors(awg):
    error = awg.query('system:error:all?')
    print('Status: {}'.format(error))
