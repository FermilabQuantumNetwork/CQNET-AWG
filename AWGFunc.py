import numpy as np

#awg.write('*rst')
#awg.write('*cls')
sampleRate = 25e9
Vmin=-.200

def createWaveformTwoPulse(repRate,pulseWidth,pulseSep,Vmin, Vmax):
    numSamples=round(sampleRate/repRate)
    return np.zeros()

def createMarker1(lengthOnes, wfLength):
    return np.ones()

def createMarker2(length):
    return np.zeros(length)


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

def loadWaveform(awg, name):
    return awg.write('source1:waveform "{}"'.format(name))


def checkErrors(awg):
    error = awg.query('system:error:all?')
    print('Status: {}'.format(error))
