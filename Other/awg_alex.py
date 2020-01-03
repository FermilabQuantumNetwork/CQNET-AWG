# Alex's working code for controlling the AWG

import numpy as np
from qcodes.instrument_drivers.tektronix.AWG70002A import AWG70002A
import pyvisa as visa
import time

awg = AWG70002A('awg', 'TCPIP0::192.168.0.165::inst0::INSTR')
rm = visa.ResourceManager('@py')
awg1 = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')

awg.mode('AWG')
awg.ch1.resolution(8)
awg.clearSequenceList()
awg.clearWaveformList()


N = 2400
m1 = np.concatenate((np.ones(int(N/2)), np.zeros(int(N/2))))
m2 = np.concatenate((np.zeros(int(N/2)), np.ones(int(N/2))))
ramp = 0.075*np.linspace(0, 1, N)
mysine = 0.1*np.sin(10*2*np.pi*np.linspace(0, 1, N)) + ramp
data = np.array([mysine, m1, m2])


filename = 'wvf_alex.wfmx'
#wfmx_file = awg.makeWFMXFile(data, 0.350)
#awg.sendWFMXFile(wfmx_file, filename)
#awg.loadWFMXFile(filename)





print(awg.waveformList)

awg.ch1.setWaveform(filename.replace('.wfmx', ''))
awg.ch1.state(1)
awg.ch1.state(0)
