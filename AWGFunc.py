#Functions for creating, sending, loading, and running waveforms/markers on the AWG.
#This code is for a Tektronix AWG70002A.
import numpy as np
awg_sampleRate = 25e9 #in Hz
midway=0.5
awg_Vmin=-0.250 #in volts
awg_Vmax=0.250 #in volts

#Variables:
#repRate = repetition rate (Hz)
#pulseWidth = pulse width (seconds)
#pulseCenter = start position of pulse in terms of fraction of clock cycle
#Vmin = minimum voltage of waveform (volts)
#Vmax = max voltage of waveforms (volts)
#sampleRate = sample rate (Hz)


#Creates an waveform with a single pulse.
def createWaveformOnePulseArray(repRate, pulseWidth, pulseCenter = midway, Vmin=awg_Vmin, Vmax=awg_Vmax, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate) #number of samples
    VminNorm=Vmin/awg_Vmax #normalized by amplitude
    VmaxNorm=Vmax/awg_Vmax #normalized by amplitude
    wfm_arr = VminNorm*np.ones(numSamples) #number of samples = length of voltage array
    pulseWidthSampleSize = round(pulseWidth*sampleRate) #number of samples in pulse
    pulseStartInd = round(numSamples*pulseCenter) - round(pulseWidthSampleSize/2) - 1 #Make start index so center of pulse is at pulseCenter
    pulseEndInd = pulseStartInd + pulseWidthSampleSize
    for i in range(pulseStartInd,pulseEndInd+1):
        wfm_arr[i] = VmaxNorm
    return wfm_arr



#Creates an waveform with two pulses.
def createWaveformTwoPulseArray(repRate,pulseWidth,pulseSep,pulseCenter=midway, Vmin=awg_Vmin, Vmax=awg_Vmax, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate)
    VminNorm=Vmin/awg_Vmax
    VmaxNorm=Vmax/awg_Vmax
    wfm_arr = VminNorm*np.ones(numSamples)
    print(pulseWidth*sampleRate)
    pulseWidthSampleSize = round(pulseWidth*sampleRate)
    pulseSepSampleSize = round(pulseSep*sampleRate)
    pulse1StartInd = round(numSamples*pulseCenter - pulseWidthSampleSize/2 - pulseSepSampleSize/2 - 1)
    pulse1EndInd = pulse1StartInd + pulseWidthSampleSize
    print(pulse1StartInd)
    print(pulse1EndInd)
    for i in range(pulse1StartInd,pulse1EndInd):
        wfm_arr[i] = VmaxNorm
    pulse2StartInd = round(numSamples*pulseCenter - pulseWidthSampleSize/2 + pulseSepSampleSize/2 - 1)
    pulse2EndInd = pulse2StartInd + pulseWidthSampleSize
    for i in range(pulse2StartInd,pulse2EndInd):
        wfm_arr[i] = VmaxNorm
    return wfm_arr

def createMarker1Array(repRate, onStart = midway, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate)
    marker1_arr = np.zeros(numSamples)
    onStartInd = round(onStart*numSamples) - 1
    for i in range(onStartInd,numSamples):
        marker1_arr[i] = 1
    return marker1_arr

def createMarker2Array(repRate, sampleRate=awg_sampleRate):
    numSamples = round(sampleRate/repRate)
    marker2_arr = np.zeros(numSamples)
    return marker2_arr

def createMarkerData(marker1_arr, marker2_arr):
    # Marker data is an 8 bit value. Bit 6 is marker 1 and bit 7 is marker 2
    exData1 = (1 << 6) * marker1_arr.astype(np.uint8)
    exData2 = (1 << 7) * marker2_arr.astype(np.uint8)
    markerData = exData1 + exData2
    return markerData

def sendWaveform(awg, name, recordLength, wfmArr):
    delete_wfm = 'wlist:waveform:delete "{:s}"'.format(name)
    create_wfm = 'wlist:waveform:new "{:s}", {:d}'.format(name, recordLength)
    wfm_bytes = len(wfmArr) * 4
    wfm_header = 'wlist:waveform:data "{:s}", 0, {:d}, '.format(name, recordLength, len(str(wfm_bytes)), wfm_bytes)
    awg.write(delete_wfm)
    awg.write(create_wfm)
    ret=awg.write_binary_values(wfm_header, wfmArr)
    print('Waveform bytes: {}'.format(ret))
    return ret

def sendMarkerData(awg, name, recordLength, markerData):
    marker_bytes = len(markerData) * 4
    marker_header = 'wlist:waveform:marker:data "{:s}", 0, {:d}, '.format(name, recordLength, len(str(marker_bytes)), marker_bytes)
    ret=awg.write_binary_values(marker_header, markerData,datatype='B')
    print('Marker bytes: {}'.format(ret))
    return ret

def loadWaveform(awg, name, channelNum):
    #awg.write('source1:waveform "{}"'.format(name))
    if channelNum ==1:
        return awg.write('source1:waveform "{}"'.format(name))
    elif channelNum == 2:
        return awg.write('source2:waveform "{}"'.format(name))
    else:
        print("Enter valid channel number (1 or 2)")


def checkErrors(awg):
    error = awg.query('system:error:all?')
    print('Status: {}'.format(error))
