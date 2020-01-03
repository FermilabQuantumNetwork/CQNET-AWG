# CQNET-AWG
Code for remotely controlling Tektronix AWG70002A
1. `AWGFunc.py` (Python3, Commented, INQNET1) - Contains functions for creating, sending, loading, and running waveforms based on pyvisa to remotely control AWG70k
2. `run_AWG_2pulseJan3.py` (Python3, Commented, INQNET1)- Create, send, and load waveform + marker data to Channels 1
and 2 of the AWG. Sends two pulse waveform to CH1 and one pulse waveform to CH2. For both channels, marker 1 is a pulse and marker 2 is zero.
3. `run_AWG_HOM.py` (Python3, Commented, INQNET1)- Create, send, and load waveform + marker data to Channels 1
and 2 of the AWG for HOM measurements. Sends single pulse waveforms to CH1 and CH2. For both channels, marker 1 is a pulse and marker 2 is zero.
4. `run_AWG.py` (Python3, Commented, INQNET1)- Create, send, and load waveform + marker data to Channel 1 of the AWG.

The "Other" folder contains older versions and starter codes (uncommented).
