############ Input ###############
path_in = '/dataSATA/data_synchrotron/esrf_id11_2024_07_nacre/20240706/RAW_DATA/nacre/ihmi1563_nacre.h5'
h5_proj_pattern = 'nacre_Z*.1'
h5_data_path = 'measurement/eiger'
h5_tilt_angle_path = 'instrument/positioners/alry' # tilt angle
h5_rot_angle_path = 'measurement/rot' # rotation angle
h5_ty_path = 'measurement/dty' # horizontal position
h5_tz_path = 'instrument/positioners/pz' # vertical position
h5_nfast_path = None # fast axis number of points, None if controt
h5_nslow_path = None # slow axis number of points, None if controt
h5_ion_path = 'measurement/fpico6' # photon counter if present else None

# Integration mode
mode = 2 # 1: 1D, 2: 2D, 3: both

# parallelisation
n_tasks = 8
cores_per_task = 16

# Parameters for pyFAI azimuthal integration
rad_range = [0.01, 37] # radial range
rad_unit = 'q_nm^-1' # radial parameter and unit ('q_nm^-1', ''2th_deg', etc)
azi_range = [-180, 180] # azimuthal range in degree
npt_rad = 100 # number of points radial direction
npt_azi = 120 # number of points azimuthal direction
npt_rad_1D = 2000 # number of points radial direction
int_method=('bbox','csr','cython') # pyFAI integration methods
poni_path = '/dataSATA/data_synchrotron/esrf_id11_2024_07_nacre/20240706/PROCESSED_DATA/CeO2/CeO2.poni'
mask_path = '/dataSATA/data_synchrotron/esrf_id11_2024_07_nacre/20240706/PROCESSED_DATA/CeO2/eiger_mask_E-08-0144_20240205.edf'
polarisation_factor= 0.95 # polarisation factor, usually 0.95 or 0.99
flatfield_correction = None
solidangle_correction = True
darkcurrent_correction = None
##############################