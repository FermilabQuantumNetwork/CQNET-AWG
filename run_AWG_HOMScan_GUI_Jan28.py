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
import time
import pymysql
from datetime import datetime

sampleRate = AWGFunc.awg_sampleRate
Vmin = AWGFunc.awg_Vmin
Vmax = AWGFunc.awg_Vmax
repRate = 90*10**6 #Clock rate (Hz)
clockCycle = 1/repRate
wfmPulseWidth=40e-12 #in seconds
markerPulseWidth = 600e-12

#Bob Pos
pulseCenterWfm_Ch1 = 0.5
#Bob Marker
pulseCenterMkr2_Ch1 = 0.7
#Alice Pos
pulseCenterWfm_Ch2 = 0.2912#0.23 #0.8236


delayStep = 40*10**(-12) #s
scanRange = 1700 * 10**(-12)
delayStepFrac = delayStep/clockCycle
numSteps = round(scanRange/delayStep)




def getLastDelay(db):
	with db.cursor() as cur:
		TABLE_NAME = "inqnet_gui_tab2gates_V3"
		queryGUI="SELECT * FROM "+TABLE_NAME+" ORDER BY id DESC LIMIT 1;"
		cur.execute(queryGUI)
		result=cur.fetchall()
		result=result[0]
		lastDelay=result["delayline"]
	return lastDelay



db = pymysql.connect(host="192.168.0.125",  #Replace <IP ADDRESS> with the IP of computer with database. Local host if is same computer.
					 user="inqnet1", #Replace <USERNAME> with your username
					 passwd="Teleport1536!",  #Replace <PASSWORD> with your password
					 db="INQNET_GUI",
					 charset='utf8mb4',
					 autocommit =True,
					 cursorclass=pymysql.cursors.DictCursor)


with db.cursor() as cur:


	try:


		# Set up VISA instrument object
		rm = visa.ResourceManager('@py')
		awg = rm.open_resource('TCPIP0::192.168.0.165::inst0::INSTR')
		print('Connected to ', awg.query('*idn?'))


		# Create Waveform for Channel 1
		name_ch1 = 'HOM_wfm_CH1'
		pulseSep=2e-9
		wfm_arr_ch1=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth, pulseCenter = pulseCenterWfm_Ch1) #Creates single pulse for channel 1
		numSamples_ch1 = len(wfm_arr_ch1)


		# Create Marker Data for Channel 1
		marker1_arr_ch1 = AWGFunc.createMarkerZerosArray(repRate)
		marker2_arr_ch1 = AWGFunc.createMarkerOnePulseArray(repRate,markerPulseWidth, pulseCenter = pulseCenterMkr2_Ch1) #Instead of one-sided step fxn, use pulse
		markerData_ch1=AWGFunc.createMarkerData(marker1_arr_ch1,marker2_arr_ch1)

		#Send Waveform + Markers to Channel 1
		AWGFunc.sendWaveform(awg, name_ch1, numSamples_ch1, wfm_arr_ch1)
		AWGFunc.sendMarkerData(awg, name_ch1, numSamples_ch1, markerData_ch1)


		#Load Waveform + Markers onto Channel 1
		AWGFunc.loadWaveform(awg, name_ch1, 1)







		#Create Waveform for Channel 2
		name_ch2 = 'HOM_wfm_CH2'
		wfm_arr_ch2=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth, pulseCenter=pulseCenterWfm_Ch2) #Creates single pulse for channel 2

		#wfm_arr_ch2=AWGFunc.createWaveformTwoPulseArray(repRate, wfmPulseWidth, pulseSep,Vmax = 0.23, Vmin = -0.23,pulseCenter=pulseCenterWfm_Ch2) #Creates single pulse for channel 2
		numSamples_ch2 = len(wfm_arr_ch2)


		# Create Marker Data for Channel 2
		marker1_arr_ch2 = AWGFunc.createMarkerOnePulseArray(repRate,markerPulseWidth) #Instead of one-sided step fxn, use pulse
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

#		time.sleep(5)


		initDelay = pulseCenterWfm_Ch2
		currentDelay = initDelay
		prevDelay = initDelay

		TABLE_NAME = "delays"
		query="INSERT INTO "+ TABLE_NAME +"(datetime, awg) values(NOW(), +"+str(currentDelay)+");"
		#query="UPDATE "+ TABLE_NAME +"SET datetime = NOW(), currentdelay =  "+str(currentDelay)+" where id = max(id);"
		cur.execute(query)

		print(currentDelay)

		while True:
			currentDelay=getLastDelay(db)
			delay=getLastDelay(db)*10**(-12)
			currentDelay = delay/clockCycle + initDelay

			if currentDelay != prevDelay:
				print(currentDelay)
				query="INSERT INTO "+ "delays" +"(datetime, awg) values(NOW(), +"+str(currentDelay)+");"
				cur.execute(query)

				#wfm_arr_ch2=AWGFunc.createWaveformTwoPulseArray(repRate, wfmPulseWidth, pulseSep, pulseCenter=currentDelay) #Creates single pulse for channel 2
				wfm_arr_ch2=AWGFunc.createWaveformOnePulseArray(repRate, wfmPulseWidth, pulseCenter=currentDelay) #Creates single pulse for channel 2
				numSamples_ch2 = len(wfm_arr_ch2)


				#Send Waveform + Markers to Channel 2
				AWGFunc.sendWaveform(awg, name_ch2, numSamples_ch2, wfm_arr_ch2)
				AWGFunc.sendMarkerData(awg, name_ch2, numSamples_ch2, markerData_ch2)


				#Load Waveform + Markers onto Channel 2
				AWGFunc.loadWaveform(awg, name_ch2, 2)

				awg.write('awgcontrol:run:immediate')

				AWGFunc.checkErrors(awg)

				prevDelay = currentDelay
			time.sleep(1)

	except KeyboardInterrupt:
		awg.close()
		db.close()
