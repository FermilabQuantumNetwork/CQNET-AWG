"""
https://github.com/tkzilla/visa_control_examples/blob/master/Python/AWG/awg_simple_waveform_sender.py

This code will open socket port 5025 and send *IDN to instrument.
"""


import time
import numpy
import socket
import math
import sys
import numpy as np
#import mysql.connector
import pymysql
import pyvisa as visa

db = pymysql.connect(host="<IP ADDRESS>",  #Replace <IP ADDRESS> with the IP of computer with database. Local host if is same computer.
					 user="<USERNAME>", #Replace <USERNAME> with your username
					 passwd="<PASSWORD>",  #Replace <PASSWORD> with your password
					 #auth_plugin='mysql_native_password',
					 database="teleportcommission",
					 charset='utf8mb4',
					 cursorclass=pymysql.cursors.DictCursor) # name of the data base

rm = visa.ResourceManager('@py')
awg = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')
awg.timeout = 25000
awg.encoding = 'latin_1'
awg.write_termination = None
awg.read_termination = '\n'
print('PyVISA Version:', visa.__version__)



try:

	print('Connected to ', awg.query('*idn?'))
	awg.write('*rst')
	awg.write('*cls')


	# Change these based on your signal requirements
	name = 'test_wfm'
	sampleRate = 10e6
	recordLength = 2400
	freq = 100e6

	# Create Waveform
	t = np.linspace(0, recordLength/sampleRate, recordLength, dtype=np.float32)
	wfmData = 350*np.sin(2*np.pi*freq*t).astype(np.float32)
	#wfmData = np.array(np.ones(100)).astype(np.float32)
	print(wfmData)
	wfmDataBinary=wfmData.astype(np.float32).tostring()
	print(wfmDataBinary)

	# Create Marker Data
	# Marker data is an 8 bit value. Bit 6 is marker 1 and bit 7 is marker 2
	exData1 = (1 << 6) * np.random.randint(2, size=recordLength, dtype=np.uint8)
	exData2 = (1 << 7) * np.random.randint(2, size=recordLength, dtype=np.uint8)

	markerData = exData1 + exData2
	markerDataBinary=markerData.astype(np.float32).tostring()
	# print(markerDataBinary)

	# Send Waveform Data
	awg.write('wlist:waveform:new "{}", {}'.format(name, recordLength))
	stringArg = 'wlist:waveform:data "{}", 0, {}, '.format(name, recordLength)
	print(awg.write_binary_values(stringArg, wfmDataBinary))


	# # Send Marker Data
	stringArg = 'wlist:waveform:marker:data "{}", 0, {}, '.format(name, recordLength)
	awg.write_binary_values(stringArg, markerDataBinary)#, datatype='B')
	#
	#


	# Send Marker Data
	# stringArg = 'wlist:waveform:marker:data "{}", 0, {}, '.format(name, recordLength)
	#
	# awg.write_binary_values(stringArg, markerData, datatype='B')
	#

	# Load waveform, being playback, and turn on output
	awg.write('source1:waveform "{}"'.format(name))
	# awg.write('awgcontrol:run:immediate')
	# #awg.write('output1 on')

	# Check for errors
	error = awg.query('system:error:all?')
	print('Status: {}'.format(error))

	awg.close()

except KeyboardInterrupt:
		print("")
		print("quit")
		awg.close()
