#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 20:10:58 2022

@author: jacobharburg, htomio
"""

import numpy as np
import OLBtools as olb
import matplotlib.pyplot as plt
import APDtools.SAR3000_gain_model_v4 as apdtools

## TODOS - figure out interp issue
## TODOS - add atmosphere loss from modtran
## TODOS - come up with values that make sense
## TODOS - write up and summarize the 

###
### Constants ### 
###

wavelength = 1064e-9 #m
altitude = 500e3 #m

# minimum elevation of 0 deg, maximum elevation of 90 deg
elevation = np.linspace(olb.radians(90), olb.radians(5), 100)
# elevation = olb.radians(90) #deg (to radians)

zenith = np.pi/2 - elevation
slant_range = olb.slant_range(0, altitude, zenith, olb.Re)

# slant_range = np.linspace(350e3, 2000e3, 100)
pointing_loss = 3 #dB TBR
atmospheric_loss = 3 #dB TBR

# TODO - receive diameter is 5 - 8 mm, update based on Shreeyam's design
rx_d = 0.00127 #m
# D = f/N = 1.8 mm / 1.4 = 1.27 mm diameter

Vbias = 320 #V
Resp = 0.45
Rq = 1e5# 1 MOhm

apd_model = apdtools.APD_model()
Vbias_apd, P_apd = apd_model.APDcurve(Vbias, Resp, Rq)

# plt.figure()
# plt.plot(Vbias_apd, P_apd)
# plt.xlabel('APD bias, V')
# plt.ylabel('Optical power, W')

# plt.figure()
# plt.semilogx(P_apd, Vbias_apd)
# plt.xlabel('Optical power, W')
# plt.ylabel('APD bias, V')

# plt.figure()
# plt.plot(np.flip(P_apd), np.flip(Vbias_apd))
# plt.xlabel('Optical power, W')
# plt.ylabel('APD bias, V')


# ###
# ### Case 0 - mobile user at zenith
# ###

# W0 =  0.02/2 #aperture radius (m)
# tx_power = 900e-3 #W (average power)
 
# distance = 500000
# print('Slant range: %f km' % (distance/1e3))

# range_loss = olb.path_loss_gaussian(W0, wavelength, distance, rx_d, 0)
# all_losses = range_loss-pointing_loss-atmospheric_loss

# print('Range loss (factor): %e' % 10**(range_loss/10))
# print('Link gain: %f dB' % all_losses)

# rx_power = tx_power*10**(all_losses/10)
# print('Power received: %f nW' % (rx_power*1e9))


###
### Case 1 - mobile user as a function of slant range ### 
###
W0 =  0.02/2 #aperture radius (m)
# tx_power = 900e-3 #W (average power)
tx_power = 50e3 #W (peak power)

range_loss = olb.path_loss_gaussian(W0, wavelength, slant_range, rx_d, 0)
all_losses = range_loss-pointing_loss-atmospheric_loss
rx_power_1 = tx_power*10**(all_losses/10)


# Vbias_rx_1 = np.interp(rx_power_1, np.flip(P_apd), np.flip(Vbias_apd))
# Vbias_rx_1 = np.interp(rx_power_1, np.flip(P_apd), np.flip(Vbias_apd), Vbias, 0)

# Iapd_1 = apd_model.Iapd(Resp, Vbias_rx_1, rx_power_1)

Vbias_rx_1, Iapd_1, gain_1 = apd_model.Iapd_new(rx_power_1, Vbias, Resp, Rq)

# plt.figure()
# plt.plot(slant_range/1e3,rx_power_1*1e9)
# plt.xlabel('Range (km)')
# plt.ylabel('Recieved Power (nW)')


###
### Case 2 - light ground station as function of slant range ### 
###
W0 =  0.28/2 #aperture radius (m)
# tx_power = 900e-3 #W (average power)
tx_power = 50e3 #W (peak power)

range_loss = olb.path_loss_gaussian(W0, wavelength, slant_range, rx_d, 0)
all_losses = range_loss-pointing_loss-atmospheric_loss
rx_power_2 = tx_power*10**(all_losses/10)

# Vbias_rx_2 = np.interp(rx_power_2, np.flip(P_apd), np.flip(Vbias_apd))
# Vbias_rx_2 = np.interp(rx_power_2, np.flip(P_apd), np.flip(Vbias_apd), Vbias, 0)

# Iapd_2 = apd_model.Iapd(Resp, Vbias_rx_2, rx_power_2)

Vbias_rx_2, Iapd_2, gain_2 = apd_model.Iapd_new(rx_power_2, Vbias, Resp, Rq)

# plt.figure()
# plt.plot(slant_range/1e3,rx_power_2*1e9)
# plt.xlabel('Range (km)')
# plt.ylabel('Recieved Power (nW)')


###
### Case 3 - SLR as function of slant range ### 
###

W0 =  0.093/2 #aperture radius (m) but should be 1/e2 beam radius
tx_power = 1.333e9 #W (average power)

range_loss = olb.path_loss_gaussian(W0, wavelength, slant_range, rx_d, 0)
all_losses = range_loss-pointing_loss-atmospheric_loss - 40
rx_power_3 = tx_power*10**(all_losses/10)

# Vbias_rx_3 = np.interp(rx_power_3, np.flip(P_apd), np.flip(Vbias_apd))
# Vbias_rx_3 = np.interp(rx_power_3, np.flip(P_apd), np.flip(Vbias_apd), Vbias, 0)

# Iapd_3 = apd_model.Iapd(Resp, Vbias_rx_3, rx_power_3)

Vbias_rx_3, Iapd_3, gain_3 = apd_model.Iapd_new(rx_power_3, Vbias, Resp, Rq)

# plt.figure()
# plt.plot(slant_range/1e3,rx_power_3*1e9)
# plt.xlabel('Range (km)')
# plt.ylabel('Recieved Power (nW)')


###
### Case 4 - mobile aggressor as function of slant range ### 
###

W0 =  0.30/2 #aperture radius (m)
tx_power = 300e3 #W (average power)

range_loss = olb.path_loss_gaussian(W0, wavelength, slant_range, rx_d, 0)
all_losses = range_loss-pointing_loss-atmospheric_loss - 40 
rx_power_4 = tx_power*10**(all_losses/10)

# Vbias_rx_4 = np.interp(rx_power_4, np.flip(P_apd), np.flip(Vbias_apd))
# Vbias_rx_4 = np.interp(rx_power_4, np.flip(P_apd), np.flip(Vbias_apd), Vbias, 0)

# Iapd_4 = apd_model.Iapd(Resp, Vbias_rx_4, rx_power_4)

Vbias_rx_4, Iapd_4, gain_4 = apd_model.Iapd_new(rx_power_4, Vbias, Resp, Rq)

# plt.figure()
# plt.plot(slant_range/1e3,rx_power_4*1e9)
# plt.xlabel('Range (km)')
# plt.ylabel('Recieved Power (nW)')


###
### Case 5 - SLR aggressor as function of slant range ### 
###

W0 =  1/2 #aperture radius (m)
tx_power = 300e3 #W (average power)

range_loss = olb.path_loss_gaussian(W0, wavelength, slant_range, rx_d, 0)
all_losses = range_loss-pointing_loss-atmospheric_loss - 40
rx_power_5 = tx_power*10**(all_losses/10)

# Vbias_rx_5 = np.interp(rx_power_5, np.flip(P_apd), np.flip(Vbias_apd))
# Vbias_rx_5 = np.interp(rx_power_5, np.flip(P_apd), np.flip(Vbias_apd), Vbias, 0)

# Iapd_5 = apd_model.Iapd(Resp, Vbias_rx_5, rx_power_5)

Vbias_rx_5, Iapd_5, gain_5 = apd_model.Iapd_new(rx_power_5, Vbias, Resp, Rq)

# plt.figure()
# plt.plot(slant_range/1e3,rx_power_5*1e9)
# plt.xlabel('Range (km)')
# plt.ylabel('Recieved Power (nW)')

###
### Plot all cases ### 
###
plt.figure()
plt.semilogy(slant_range/1e3,rx_power_1,label='Mobile User')
plt.semilogy(slant_range/1e3,rx_power_2,label='Light GS')
plt.semilogy(slant_range/1e3,rx_power_3,label='SLR')
plt.semilogy(slant_range/1e3,rx_power_4,label='Mobile Aggressor')
plt.semilogy(slant_range/1e3,rx_power_5,label='SLR Aggressor')
plt.xlabel('Range (km)')
plt.ylabel('Recieved Average Power (W)')
plt.legend()

plt.figure()
plt.plot(slant_range/1e3,Vbias_rx_1,label='Mobile User')
plt.plot(slant_range/1e3,Vbias_rx_2,label='Light GS')
plt.plot(slant_range/1e3,Vbias_rx_3,label='SLR')
plt.plot(slant_range/1e3,Vbias_rx_4,label='Mobile Aggressor')
plt.plot(slant_range/1e3,Vbias_rx_5,label='SLR Aggressor')
plt.xlabel('Range (km)')
plt.ylabel('Bias Voltage(V)')
plt.legend()

plt.figure()
plt.plot(slant_range/1e3,gain_1,label='Mobile User')
plt.plot(slant_range/1e3,gain_2,label='Light GS')
plt.plot(slant_range/1e3,gain_3,label='SLR')
plt.plot(slant_range/1e3,gain_4,label='Mobile Aggressor')
plt.plot(slant_range/1e3,gain_5,label='SLR Aggressor')
plt.xlabel('Range (km)')
plt.ylabel('Gain')
plt.legend()

plt.figure()
plt.semilogy(slant_range/1e3,Iapd_1,label='Mobile User')
plt.semilogy(slant_range/1e3,Iapd_2,label='Light GS')
plt.semilogy(slant_range/1e3,Iapd_3,label='SLR')
plt.semilogy(slant_range/1e3,Iapd_4,label='Mobile Aggressor')
plt.semilogy(slant_range/1e3,Iapd_5,label='SLR Aggressor')
plt.xlabel('Range (km)')
plt.ylabel('Current on Detector (A)')
plt.legend()



