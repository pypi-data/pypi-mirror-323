import os
import fabio
import h5py
import pyFAI
from time import time
import numpy as np
from subprocess import Popen
import shutil

from . import handle as hdl
from . import misc as msc

def start_integration( sample_dir ):
    # read and edit integration_parameters.py
    intpar_path_sample = os.path.join(sample_dir,'integration_parameters.py')
    # check if there is already an integration file
    if not os.path.isfile( intpar_path_sample ):
        intpar_path_module = hdl.get_file_path('textom',os.path.join('input','integration_parameters.py'))
        hdl.open_with_editor(intpar_path_module) # take the one from the textom module
        shutil.copyfile(intpar_path_module, intpar_path_sample ) # copy to the sample diractory
    else:
        msc.cp_add_dt(intpar_path_sample, sample_dir, now=False) # save the old version with modification date
        hdl.open_with_editor(intpar_path_sample) # edit and use the same file
    par = msc.import_module_from_path('integration_parameters', intpar_path_sample)
    print('Starting parallel pyFAI integration')
    t0 = time()
    print(f'\tSaved integration parameters to {sample_dir}') 

    # get mask and save its azimutal integration for further analysis
    mask = fabio.open(par.mask_path).data
    ai = pyFAI.load(par.poni_path)
    mask_cake = ai.integrate2d(
        np.ones_like(mask), 
        par.npt_rad, 
        par.npt_azi, 
        radial_range = par.rad_range, 
        azimuth_range = par.azi_range, 
        unit=par.rad_unit,
        method = par.int_method, 
        correctSolidAngle = par.solidangle_correction, 
        mask = mask, 
        safe = False,
    )
    os.makedirs(os.path.join( sample_dir, 'analysis'), exist_ok=True)
    path_mask = os.path.join( sample_dir, 'analysis', 'mask_detector_cake.h5' )
    with h5py.File(path_mask, 'w') as hf:
        hf.create_dataset('mask_cake', data = mask_cake.intensity)
    
    # start parallel integration in separate processes
    int_path = hdl.get_file_path('textom',os.path.join('src','integration_launcher.py'))
    pids = []
    for k in range(par.n_tasks):
        command = [
            'taskset', '-c', '%d-%d' % (k*par.cores_per_task, (k+1)*par.cores_per_task),
            'python', int_path, 
            '-k', '%d' % (k),
            '-d', '%s' % (sample_dir),
        ]
        p = Popen(command)
        pids.append(p)
    for p in pids: # wait for all to be finished
        p.wait()
    for p in pids: # cleanup (not really necessary)
        p.kill()
    print('Integrations finished, total time: %d s' % (time()-t0))
