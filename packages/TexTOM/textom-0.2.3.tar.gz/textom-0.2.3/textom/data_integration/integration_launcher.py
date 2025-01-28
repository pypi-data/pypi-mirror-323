# import argcomplete
import argparse, sys
import os
import re
import fabio
import h5py
import pyFAI
from time import time
import numpy as np

from textom.input.integration_parameters import *

def integration_launcher( k_task, dir_out_full ):
    
    fid_in = h5py.File( path_in, 'r' )
    repattern = '^' + h5_proj_pattern.replace('*', '(.*?)') + '$'
    repattern = re.compile(repattern)

    # get all datasets that correspond to the pattern
    filtered_datasets = []
    scan_no = []
    for entry in fid_in.keys():
        match = repattern.match(entry)
        if ( match and (int(float(entry.split('_')[5])) >= resume) ):
            if match:
                filtered_datasets.append(entry)
                try:
                    scan_no.append(int(match.group(1)))
                except:
                    pass
    
    flat=None
    if isinstance( flatfield_correction, str ):
        flat = fabio.open(flatfield_correction).data

    mask = fabio.open(mask_path).data
    ai = pyFAI.load(poni_path)
    mask_cake = ai.integrate2d(
        np.ones_like(mask), 
        npt_rad, 
        npt_azi, 
        radial_range = rad_range, 
        azimuth_range = azi_range, 
        unit=rad_unit,
        method = int_method, 
        correctSolidAngle = solidangle_correction, 
        dark = darkcurrent_correction,
        # flat = flat,
        mask = mask, 
        polarization_factor = polarisation_factor, 
        safe = False,
    )

    # ######################## development of adapting the mask for textom
    # import numpy as np
    # mc = mask_cake.intensity.copy()
    # mc[mc>1e-2] = 1
    # mask_detector = np.genfromtxt('/dataSATA/data_synchrotron/esrf_id13_2024_2_enthesis/20240215/PROCESSED_DATA/biomorph_blobb/analysis/fit_detmask.txt', bool)
    # import matplotlib.pyplot as plt
    # from matplotlib import colors

    # plt.figure()
    # plt.matshow(mask)
    # f,ax=plt.subplots()
    # im = ax.matshow(mc, norm=colors.LogNorm())
    # f.colorbar(im)
    # f,ax=plt.subplots()
    # ax.imshow(mask_detector.reshape((8,120)).T)
    # fig = plt.figure()
    # ax = fig.add_subplot(projection='polar')
    # phi = np.linspace(*azi_range, num=npt_azi)*np.pi/180
    # q = np.linspace(*rad_range, num=npt_rad)
    # PHi, QQ = np.meshgrid( phi, q )
    # ax.pcolormesh(PHi, QQ, mc.T)
    # plt.show()

    # peak_reg = np.genfromtxt('/dataSATA/data_synchrotron/esrf_id13_2024_2_enthesis/20240215/PROCESSED_DATA/biomorph_blobb/analysis/peak_regions.txt')
    # qm = [np.logical_and(QQ >= start, QQ <= end) for start,end in peak_reg]
    # mask_qregrouped = np.array([
    #     [np.logical_and.reduce(mc[k, qm[l][:,k]]) for k in range(npt_azi)] 
    #         for l in range(len(peak_reg))])
    # ########################

    os.path.mkdirs(os.path.join( dir_out_full, 'analysis'), exist_ok=True)
    path_mask = os.path.join( dir_out_full, 'analysis', 'mask_detector_cake.h5' )
    with h5py.File(path_mask, 'w') as hf:
        hf.create_dataset('mask_cake', data = mask_cake.intensity)

    t0 = time()
    cnt = 0
    n_tot = len(filtered_datasets)
    for l in range ( k_task, n_tot, n_tasks):
        try:
            # get paths for the correct h5 file
            h5path_data = '{}/{}'.format(filtered_datasets[l],h5_data_path)
            h5path_ty = '{}/{}'.format(filtered_datasets[l],h5_ty_path)
            h5path_tz = '{}/{}'.format(filtered_datasets[l],h5_tz_path)
            h5path_fov0 = '{}/{}'.format(filtered_datasets[l],h5_fov0_path)
            h5path_fov1 = '{}/{}'.format(filtered_datasets[l],h5_fov1_path)
            h5path_ion = '{}/{}'.format(filtered_datasets[l],h5_ion_path)

            # for writing:
            scan = True
            try:
                fov = ( fid_in[h5path_fov0][()], fid_in[h5path_fov1][()]  )
                ty = fid_in[h5path_ty][()]
                tz = fid_in[h5path_tz][()]
                ion = fid_in[h5path_ion][()]
            except:
                scan=False

            if isinstance(h5_tilt_angle_path,str) and isinstance(h5_rot_angle_path,str):
                h5path_tilt = '{}/{}'.format(filtered_datasets[l],h5_tilt_angle_path)
                h5path_rot = '{}/{}'.format(filtered_datasets[l],h5_rot_angle_path)

                out_name = '{}_{:03d}_{:03d}_{:.0f}_{:08.2f}_diff_scan_0001_comb'.format(
                            title,
                            scan_no[l],scan_no[l],
                            fid_in[h5path_tilt][()],
                            fid_in[h5path_rot][()],
                        ).replace('.','p')
            else:
                out_name = filtered_datasets[l][:-2]

            data_in = fid_in[h5path_data]
            n_frames = data_in.shape[0]

            if mode%2:
                os.makedirs(os.path.join(dir_out_full, 'data_integrated_1d/'), exist_ok=True)
                path_out = os.path.join(
                    dir_out_full, 'data_integrated_1d/',
                    out_name + '_integrate_1d.h5'
                )
                fid_out = h5py.File( path_out, 'w' )
                radial_dset = fid_out.create_dataset( 'radial_units', (1,npt_rad_1D) )
                intensity_dset = fid_out.create_dataset(
                    'cake_integ',
                    ( n_frames, npt_rad_1D ),
                    chunks = ( 1, npt_rad_1D ),
                    shuffle="True", compression="lzf"
                    )


                t0 = time()
                for frame in range (0,n_frames):
                    # print(frame)
                        
                    result1D = ai.integrate1d(
                        data_in[frame,:,:], 
                        npt_rad_1D, 
                        radial_range = rad_range, 
                        unit=rad_unit,
                        method = int_method, 
                        correctSolidAngle = solidangle_correction, 
                        dark = darkcurrent_correction,
                        flat = flat,
                        mask = mask, 
                        polarization_factor = polarisation_factor, 
                        safe = False,
                    )

                    radial_dset[0,:] = result1D.radial
                    intensity_dset[frame,:]= result1D.intensity

                if scan:
                    # Write some metadata
                    fid_out.create_dataset( 'ty', data= ty )
                    fid_out.create_dataset( 'tz', data= tz )
                    fid_out.create_dataset( 'fov', data=fov )
                    fid_out.create_dataset( 'ion', data=ion )

                ai.reset()
                fid_out.close()  
    
            if mode>1:
                os.makedirs(os.path.join(dir_out_full, 'data_integrated/'), exist_ok=True)
                path_out = os.path.join(
                    dir_out_full, 'data_integrated/',
                    out_name + '_integrate_2d.h5'
                )
                fid_out = h5py.File( path_out, 'w' )

                if scan:
                    # Write some metadata
                    fid_out.create_dataset( 'ty', data= ty )
                    fid_out.create_dataset( 'tz', data= tz )
                    fid_out.create_dataset( 'fov', data=fov )
            

                radial_dset = fid_out.create_dataset( 'radial_units', (1,npt_rad) )
                azimuthal_dset = fid_out.create_dataset( 'azimuthal_units', (1,npt_azi) )
                intensity_dset = fid_out.create_dataset(
                        'cake_integ',
                        ( n_frames, npt_azi, npt_rad ),
                        chunks = ( 1, npt_azi, npt_rad ),
                        shuffle="True", compression="lzf"
                        )
              
                t0 = time()
                for frame in range (0,n_frames):
                    # print(frame)
                    # print(npt_rad)
                    # print(npt_azi)
                    # print(rad_range)
                    # print(azi_range)
                    # print(rad_unit)
                    # print(int_method)
                    # print(solidangle_correction)
                    # print(darkcurrent_correction)
                    # print(flatfield_correction)
                    # print(mask)
                    # print(polarisation_factor)
                
                    result2D = ai.integrate2d(
                        data_in[frame,:,:], 
                        npt_rad, 
                        npt_azi, 
                        radial_range = rad_range, 
                        azimuth_range= azi_range, 
                        unit=rad_unit,
                        method = int_method, 
                        correctSolidAngle = solidangle_correction, 
                        dark = darkcurrent_correction,
                        flat = flat,
                        mask = mask, 
                        polarization_factor = polarisation_factor, 
                        safe = False,
                    )

                    radial_dset[0,:] = result2D.radial
                    azimuthal_dset[0,:] = result2D.azimuthal
                    intensity_dset[frame,:,:]= result2D.intensity
                
                ai.reset()
                fid_out.close()
        except:
            pass
        
        cnt += 1
        print('\tTask %d: %d/%d done, av. time per scan: %.2f s' % (
            k_task, l+1, n_tot, (time()-t0)/cnt))
    fid_in.close()

            # path_out = os.path.join(
            #     dir_out_full,
            #     'scan_%04d_int2D.h5' % (l),
            #     )

            # radial_dset = fid_out.create_dataset( rad_unit, (1,npt_rad) )
            # azimuthal_dset = fid_out.create_dataset( 'phi_deg', (1,npt_azi) )
            # intensity_dset = fid_out.create_dataset(
            #     'intensity',
            #     ( n_frames, npt_azi, npt_rad ),
            #     chunks = ( 1, npt_azi, npt_rad ),
            #     shuffle="True", compression="lzf"
            #     )       

            # tscan2D = integrate_pyFAI_2D(
            #     flist[l], h5_internal_path,
            #     path_out, 
            #     rad_range, azi_range, 
            #     rad_unit, 
            #     npt_rad, npt_azi, 
            #     poni_path, mask, 
            #     int_method, 
            #     polarisation_factor, 
            #     solidangle_correction,
            #     flat,
            #     darkcurrent_correction,
            # )

# integration_launcher(1,'/dataSATA/data_synchrotron/esrf_id13_2021_11_ls3046_zlotnikov/20211104/PROCESSED_DATA/b1_block000/')
integration_launcher(2,'/dataSATA/data_synchrotron/esrf_id13_2024_2_enthesis/20240215/PROCESSED_DATA/biomorph_blobb')
                     
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--k_task", type=int, default=0)
    parser.add_argument("-d", "--dir_out_full", type=str, default=0)
    # argcomplete.autocomplete(parser)
    args = parser.parse_args()

    integration_launcher(args.k_task,args.dir_out_full)

if __name__ == "__main__":
    main(sys.argv[1:])