import numpy as np
import scipy.special as scsp
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mpc

import OLBtools as olb

##### OCTL Beacon Laser Transmitter
# Beacon laser power, W
P_tx = 5e3          # 5 kW assumption for OCTL
# Beacon laser wavelenght, m
lambda_gl = 1064e-9 # 1064 nm
# Beacon laser beam width, FWMH radian
beam_width = 40e-6  # 40-100 urad for OCTL
# Transmitter implementation loss, dB
tx_impl_loss = 2  # 2 dB estimate
# Transmitter pointing loss, dB
tx_pointing_loss = 2  # 2 dB estimate
# Atmosphere loss, dB
atmosphere_loss = 4  # 5 dB estimate
# Pulse duration, s
pulse_duration = 12.5e-6 # 12.5 us for 4 kHz

##### CubeSat Receiver
# Cubesat receiver aperture diameter, m
aperture = 0.1      # 10 cm assumption
# Receiver system loss, dB
rx_system_loss = 3  # 3 dB estimate

# Link distance, m
link_range_min = (0.002)*(1.495978707e11)   # Lunar distance, 0.002 AU
link_range_max = (1)*(1.495978707e11)   # Mars-ish distance, 1 AU

c = 299800000
frequency = c/lambda_gl
planck_constant = 6.26e-34
photon_energy = frequency*planck_constant

#----------------------------------------------------------
#500 poitnts, from minimum link range to maximum
link_range = np.linspace(link_range_min,link_range_max,500)

# beam waist
W_0 = olb.fwhm_to_radius(beam_width,lambda_gl)

# Angular wave number, = 2*pi/lambda
k = olb.angular_wave_number(lambda_gl)

range_loss = olb.path_loss_gaussian(W_0, lambda_gl, link_range, aperture)

all_losses = range_loss-tx_impl_loss-tx_pointing_loss-atmosphere_loss-rx_system_loss

P_rx = P_tx*10**(all_losses/10)


pulse_energy = P_rx*pulse_duration
photon_count = pulse_energy/photon_energy

link_range_au = link_range/(1.495978707e11)

# print('Range loss: %.3f dB' % (range_loss))
# print('All losses loss: %.3f dB' % (all_losses))
# print('Received power: %.3f uW' % (P_rx*1e6))

fig,ax = plt.subplots()
ax.plot(link_range_au, P_rx)

ax.set_yscale('log')
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.set_xlabel('Link Range [AU]',fontsize=14)
ax.set_ylabel('Received Power [W]',fontsize=14)
ax2 = ax.twinx()

ax2.set_yscale('log')
ax2.tick_params(axis='y', labelsize=12)
ax2.plot(link_range_au, photon_count)
ax2.set_ylabel('Received Photons [count]',fontsize=14)

plt.title('Uplink Received Power, Photon Count Over Link Range',fontsize=16)

plt.show()

fig.savefig('uplink3.png',
            format='png',
            dpi=300,
            bbox_inches='tight')
