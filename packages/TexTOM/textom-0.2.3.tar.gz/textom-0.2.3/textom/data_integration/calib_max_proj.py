import matplotlib.pyplot as plt
import h5py
import numpy as np 
import fabio
import os
#from scipy import ndimage
####
# ['acq_time_3', 'counter1', 'counter2', 'ct32', 'ct34', 'eiger',
#   'eiger_hap002', 'eiger_hap002_avg', 'eiger_hap002_max', 'eiger_hap002_min', 
#   'eiger_hap002_std', 'eiger_saxs', 'eiger_saxs_avg', 
#  'eiger_saxs_max', 'eiger_saxs_min', 'eiger_saxs_std', 'fx1_det0', 
#  'fx1_det0_BaL', 'fx1_det0_Br', 'fx1_det0_Ca', 'fx1_det0_Cu', 
#  'fx1_det0_Fe', 'fx1_det0_K', 'fx1_det0_Mn', 'fx1_det0_Ni', 'fx1_det0_Rb', 
#  'fx1_det0_S', 'fx1_det0_Se', 'fx1_det0_Si', 'fx1_det0_Sr', 'fx1_det0_Ti', 
#  'fx1_det0_Zn', 'fx1_det0_elapsed_time', 'fx1_det0_event_count_rate', 'fx1_det0_events', 
#  'fx1_det0_fractional_dead_time', 'fx1_det0_live_time', 'fx1_det0_test', 'fx1_det0_test1',
#    'fx1_det0_trigger_count_rate', 'fx1_det0_trigger_live_time', 'fx1_det0_triggers',
#      'nnp5_position', 'nnp6_position', 'raw_adc3', 'raw_nnp5_adc', 'raw_nnp6_adc',
#        'raw_z_adc', 'time']

# stumpf hier 
import os.path
def h5file_input(filename, data, ds_name):
# creates h5 file, deletes and submits if key already exists

    if os.path.exists(filename):
        with h5py.File(filename, 'a') as f:
            if ds_name in f.keys():
                del f[ds_name]
                f.create_dataset(ds_name, data = data.astype(np.float64))
            else:
                f.create_dataset(ds_name, data = data.astype(np.float64))
    else:
        with h5py.File(filename, 'w') as f:
            f.create_dataset(ds_name, data = data.astype(np.float64))
    f.close()
    
    
    
calib_h5file =    '/data/visitor/ls3299/id13/20240215/RAW_DATA/calib_al2o3/ls3299_calib_al2o3.h5'
    
roi_values_path = '/measurement/eiger_saxs'# change this to get different maps 
outdir = '/data/visitor/ls3299/id13/20240215/PROCESSED_DATA/calibs/'
os.makedirs(outdir, exist_ok=True)
#"/data/visitor/ls3299/id13/20240215/RAW_DATA/calib_al2o3/ls3299_calib_al2o3.h5"

	

with h5py.File(calib_h5file, 'r') as f:
	
	list_keys = f.keys()
	list_keys = [l for l in list_keys if 'al2o3_al2o3' in l]

	
	
	for calib_name in list_keys:
		print(calib_name)
		#calib_name = 'calib_al2o3_al2o3_m200_2.1'
		try:
			calib_array = f['%s'%calib_name]['measurement']['eiger'][...]


			calib_array_max = calib_array.max(axis =0)

			h5file_input(outdir+'%s.h5'%calib_name, calib_array_max, 'max_proj')
		except:
			continue

