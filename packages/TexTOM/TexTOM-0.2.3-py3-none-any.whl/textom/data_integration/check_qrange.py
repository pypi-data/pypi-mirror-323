import pyFAI
import pyFAI.azimuthalIntegrator
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import h5py

# Load the .poni file
poni_path = '/dataSATA/data_synchrotron/esrf_id13_2024_05_ch7039_enthesisII/20240501/PROCESSED_DATA/calibs/m200.poni'
ai = pyFAI.load(poni_path)

data_file = '/dataSATA/data_synchrotron/esrf_id13_2024_05_ch7039_enthesisII/20240501/RAW_DATA/s3hur4/s3hur4_tt_s3hur4_ttomo_a_027_027_0_00097p20_diff/scan00003/eiger/s3hur4_tt_s3hur4_ttomo_a_027_027_0_00097p20_diff_00003_data_000000.h5'
with h5py.File(data_file) as hf:
    # data = hf['entry_0000/measurement/data'][50,:,:]
    data = hf['entry_0000/measurement/data'][50,:,:]

# Perform azimuthal integration
result2D = ai.integrate2d(
    data, 
    512, 
    60, 
    radial_range = [0.5, 44.5], 
    azimuth_range= [-180,180], 
    unit='q_nm^-1',
    method = ('bbox','csr','cython'), 
    # correctSolidAngle = solidangle_correction, 
    # dark = darkcurrent_correction,
    # flat = flat,
    # mask = mask, 
    # polarization_factor = polarisation_factor, 
    # safe = False,
)
q = result2D.radial
chi = result2D.azimuthal
I = result2D.intensity
Chi,Q = np.meshgrid(chi,q)

maxval = I.max()
lognrm = colors.LogNorm(vmin=1, vmax=3)

# Plot the result
plt.figure()
plt.pcolormesh( Q, Chi, I.T, 
               norm=lognrm, 
               cmap='plasma')
# plt.xscale('log')
plt.xlabel('q (1/nm)')
plt.ylabel('chi (rad)')
plt.title('Azimuthal Integration')
plt.show()