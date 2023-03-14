#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 17:23:35 2023

@author: htomio
"""
import sys
import OLBtools as olb
import numpy as np
import math

from tabulate import tabulate
from scipy.signal import welch
import matplotlib.pyplot as plt

## Add path to PyDSP
sys.path.append(r"C:\Users\Hannah\Documents\workspace")

from PyDSP_core.TX.Tx_generateBits import Tx_generateBits, nextpow2
from PyDSP_core.TX.setSignalParams import setSignalParams
from PyDSP_core.TX.pulseShaper import pulseShaper
from PyDSP_core.TX.QAM_config import QAM_config
from PyDSP_core.TX.Tx_QAM import Tx_QAM
from PyDSP_core.TX.laserCW import laserCW

from PyDSP_core.RX.setSNR import setSNR

from PyDSP_core.DSP.symDemapper import symDemapper
from PyDSP_core.DSP.rxDecision import BER_eval, EVM_eval, MI_eval
from PyDSP_core.DSP.LPF_apply import LPF_apply


#----------------------------------------------------------
# LINK
#----------------------------------------------------------

# Transmit
wavelength = 1550e-9 # m
tx_power = 100e-3 # W
tx_beam_diam = 3e-2 # 1/e2 diameter, m
tx_system_loss = 1 # dB

# Receive
rx_aperture_diam = 3e-2 # clear glass aperture, diameter, m
rx_system_loss = 1 # dB

# Pointing and link gemotry
pointing_loss = 3 #dB
link_range = 1e6 # m


tx_power = 300e-3 #W (average power)
pointing_loss = 3 #dB
atmospheric_loss = 0 #dB (set to zero for now)
W0 =  0.02/2 #aperture radius (m)


range_loss = olb.path_loss_gaussian(tx_beam_diam, wavelength, link_range, rx_aperture_diam, 0)

all_losses = range_loss-pointing_loss-atmospheric_loss
print('Link gain: %f dB' % all_losses)

rx_power = tx_power*10**(all_losses/10)
print('Power received: %f nW' % (rx_power*1e9))

SNR_dB = 10*np.log10(rx_power)
print('Power received: %f dB' % (SNR_dB))

#----------------------------------------------------------
# COHERENT
#----------------------------------------------------------

### Transmitter Parameters

#Signal Parameters:
SIG = {
    'M': 16,            #QAM constellation size
    'symRate': 60e9,    #total symbol-rate of the signal
    'modulation': 'QAM',#modulation type [QAM/PAM]
    'rollOff': 0.1,     #roll-off factor
    'nPol': 1,          #number of polarizations
    'nSyms': pow(2, 17) #total number of simulated symbols
}
nSpS = 2                #number of samples per symbol
laserLW = 1e3           #laser linewidth [Hz]
TX = {'SIG': setSignalParams('symRate', SIG['symRate'], 'M', SIG['M'], 'nPol', SIG['nPol'],
                             'nBpS', math.log2(SIG['M']), 'nSyms', SIG['nSyms'],
                             'roll-off', SIG['rollOff'], 'modulation', SIG['modulation'])
}

#Modulation Parameters:
TX['QAM'] = QAM_config(TX['SIG'])
#Bit Parameters:
TX['BIT'] = {'source': 'randi',
             'seed': 1
}
#Pulse Shaping Filter Parameters:
TX['PS'] = {'type': 'RRC',
            'rollOff': TX['SIG']['rollOff'],
            'nTaps': 128
}
#DAC Parameters:
TX['DAC'] = {'RESAMP': {'sampRate':nSpS * TX['SIG']['symRate']}
}
#Laser Parameters:
TX['LASER'] = {
    'linewidth': laserLW,
}

### DSP Parameters

#Matched-Filter Parameters:
DSP = {'MF':{'type': 'RRC',
             'rollOff': TX['SIG']['rollOff']}
}
#Carrier-Phase Estimation:
DSP['CPE'] = {
    'method': 'VV',
    'decision': 'QPSKpartition',
    'QAM_classes': 'all',
    'nTaps': 50
}
#Demapper:
DSP['DEMAPPER'] = {
    'normMethod': 'MMSE'
}

### Generate TX Bits
TX['BIT']['txBits'] = Tx_generateBits(SIG['nSyms'], TX['QAM']['M'], TX['QAM']['nPol'], TX['BIT'])

### Generate Transmitted Symbols
S = {}
S['tx'], TX['BIT']['txSyms'] = Tx_QAM(TX['QAM'], TX['BIT']['txBits'])

# Plot Transmitted Constellation Symbols:
plt.scatter(S['tx'].real, S['tx'].imag, s=20)
plt.title('IQ Constellation of the Transmitted Signal')
plt.show()

### Pulse Shaping
S['txSC'], TX['PS'] = pulseShaper(S['tx'], nSpS, TX['PS'])

#Plot Pulse Shaping Taps:
plt.plot(TX['PS']['W'])
plt.title('Pulse Shaping Taps')
plt.show()

# Plot Signal Spectrum:
# No matlab: pwelch(S.txSC(1,:),1e4,[],[],TX.DAC.RESAMP.sampRate,'centered')
#                  (x, window, noverlap, nfft, Fs, freqrange)
#
# window - If window is an integer, the signal is divided into segments of length window. The modified periodograms are computed using a Hamming window of length window.
# noverlap - If you do not specify noverlap, or specify noverlap as empty, the default number of overlapped samples is 50% of the window length.
# nfft - The default nfft is the greater of 256 or the next power of 2 greater than the length of the segments.

wind = np.hamming(pow(10,4))
nov = np.floor(pow(10,4)/2)
nff = max(256, pow(2,nextpow2(pow(10,4))))

f,Pxx = welch(S['txSC'][0],window = np.hamming(int(1e4)),noverlap=nov,nfft=nff,fs=TX['DAC']['RESAMP']['sampRate'],return_onesided=False ,detrend= False)
plt.plot(f,10*np.log10(Pxx))
plt.grid()
plt.show()

### Apply Laser

Fs_SC = nSpS * SIG['symRate']
nSamples = S['tx'].shape[1] * nSpS
Scw, TX['LASER'] = laserCW(TX['LASER'],Fs_SC,nSamples)
if SIG['nPol'] == 2:
    Scw = Scw/np.sqrt(2)
for n in range(0, SIG['nPol']):
    S['txSC'][n,:] = Scw*S['txSC'][n,:]

# Plot Laser Phase Noise
plt.plot(TX['LASER']['phaseNoise'],linewidth=0.5)
#plt.title('Transmitted Laser Phase Noise')
plt.xlabel('Samples')
plt.ylabel('Phase Noise')
plt.show()

### Set SNR
SNR_dB = float(SNR_dB)
S['rx'] = setSNR(S['txSC'], SNR_dB, TX['DAC']['RESAMP']['sampRate'], SIG['symRate'])[0]

### Apply Matched Filter
S['rx'] = LPF_apply(S['rx'],DSP['MF'],TX['DAC']['RESAMP']['sampRate'],SIG['symRate'])[0]

### Downsample to 1 sample/symbol
S['rx_1sps'] = S['rx'][:,::nSpS]

### Apply Symbol Demapper
C = TX['QAM']['IQmap']
DSP['DEMAPPER'],S['tx'] = symDemapper(S['rx_1sps'],S['tx'],C,DSP['DEMAPPER'])

### Performance Analysis
BER = np.zeros(SIG['nPol'])
errPos = []
EVM = np.zeros(SIG['nPol'])
MI = np.zeros(SIG['nPol'])
for n in range(0, SIG['nPol']):
    BER[n], errPos_aux = BER_eval(DSP['DEMAPPER']['txBits'][n],DSP['DEMAPPER']['rxBits'][n])
    errPos.append(errPos_aux)
    EVM[n] = EVM_eval(S['rx_1sps'][n],S['tx'][n])
    MI[n] = MI_eval(S['rx_1sps'][n],S['tx'][n],DSP['DEMAPPER']['C'][:,n],DSP['DEMAPPER']['N0'][n])
    
### Plot Constellation after Demapping
for n in range(0, SIG['nPol']):
    plt.scatter(S['rx_1sps'][n].real, S['rx_1sps'][n].imag, s=0.1)
    #plt.scatter(DSP['DEMAPPER']['C'][:,n].real, DSP['DEMAPPER']['C'][:,n].imag,s=50, marker='o', edgecolor='k', facecolor=(0,1,0,0))
    #plt.title('pol-'+str(n+1))
    plt.xlabel('Inphase')
    plt.ylabel('Quadrature')
    plt.show()
    
### Print Results
parameters = ['BER', 'EVM', 'MI']
columns = np.asarray([BER,EVM,MI])
header = [f"Polarization-{i}" for i in range(1,SIG['nPol'] + 1)]

print(tabulate(columns,headers=header,tablefmt= 'fancy_grid',showindex=parameters,numalign='right'))