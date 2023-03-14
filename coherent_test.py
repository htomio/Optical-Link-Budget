#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 17:23:35 2023

@author: htomio
"""
import OLBtools as olb
import numpy as np

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