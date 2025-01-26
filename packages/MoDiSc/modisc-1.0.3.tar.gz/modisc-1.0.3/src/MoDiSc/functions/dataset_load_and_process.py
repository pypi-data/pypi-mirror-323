#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script to load necessary files correspondig to a dataset, plus functions to reduce it via PCA, or applying a mask to the data.

Functions:
    load_PSF()
    load_SCIENCE()
    load_NOISE()
    load_PA_ARRAY()
    load_MASK2MINIMIZE()

    process_SCIENCE_PCA() -- not updated
    process_REDUCED_DATA_PCA() -- not updated
    applpy_MASK2SCIENCE() -- not updated

This script would be imported by the scripts:
    diskfit_*params_*obs.py
    plot_backend_*.py

'''

from import_functions_generic import *
import vip_hci as vip
from derive_noise_map import *
import pyregion



## Load stuff corresponding to a dataset ##
def load_PSF_one_dataset(dico = None, WRITETO=True, ID=''):
    '''
    Return the normalized PSF of the dataset. The PSF is defined as the sum of the PSF.
    The PSF is then normalized by the sum of the pixel values.
    This function differs if the data are acquired in polarised light or total intensity light.
    Save the PSF file in the path 'inputs_resultdir'.

    The center of the PSF should be on a given pixel located at x = y = n // 2 with the counting starting at 0 (so NOT between four pixels).
    
    Note: assume the following global variables to be defined before calling this function
    .DATA_DIR (string): common prefix path
    .PRE_PROCESS (string): folder in which is located the PSF (for total intensity data)
    .POST_PROCESS (string): folder in which is located the PSF (for polar data)
    .params_yaml (yaml file): configuration file in which some parameters should be defined (FN_PSF, FN_PSF_1, and/or FN_PSF_2)
    .IBAND (int): index of the band to consider
    .CROP_PSF (int): cropping value apply to the left, right, top, and botton of the image
    .display (boolean): whether to display information 
    .inputs_resultdir (string): path where to save the files
    '''
    print('\n(Load the PSF DATA)')

    # Access extra variables from dico
    display = dico.get('display', 0)
    DATADIR = dico.get('datadir', 'PROBLEM')
    FN_PSF = dico.get('fn_psf', 'PROBLEM')
    TWO_PSF_FILES = dico.get('two_psf_files', 'PROBLEM') # indicate whether there are two different files to consider for the PSF (1 = yes, 0 = no)
    FN_PSF_1 = dico.get('fn_psf_1', 'PROBLEM')
    FN_PSF_2 = dico.get('fn_psf_2', 'PROBLEM')
    CROP_PSF = dico.get('crop_psf', 'PROBLEM')
    SPATIAL_SHIFT_PSF_DATA = dico.get('spatial_shift_psf_data','PROBLEM')
    SPECTRAL_AXIS = dico.get('spectral_axis','PROBLEM')
    CHANNELS = dico.get('channels', 'PROBLEM')
    CHANNELS_COMBINED = bool(np.where(len(CHANNELS) > 1, True, False))
    inputs_resultdir = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if DATADIR == 'PROBLEM': raise ValueError('There is a problem with the value of DATADIR.')
    if type(CROP_PSF) == type(''): raise ValueError('There is a problem with the value of CROP_PSF.')
    if type(TWO_PSF_FILES) == type(''): raise ValueError('There is a problem with the value of CROP_PSF.')
    if type(SPATIAL_SHIFT_PSF_DATA) == type(''): raise ValueError('There is a problem with the value of SPATIAL_SHIFT_PSF_DATA.')
    if type(SPECTRAL_AXIS) == type('PROBLEM'): raise ValueError('There is a problem with the value of SPECTRAL_AXIS.')
    if type(CHANNELS) == type('PROBLEM'): raise ValueError('There is a problem with the value of CHANNELS.')

    if WRITETO: 
        if inputs_resultdir == 'PROBLEM': raise ValueError('There is a problem with the value of inputs_resultdir.')

    if TWO_PSF_FILES: 
        path_psf_1 = os.path.join(DATADIR, FN_PSF_1); path_psf_2 = os.path.join(DATADIR, FN_PSF_2)
        if display: print(f'The path for the PSF 1:\n {path_psf_1}\n'); print(f'The path for the PSF 2:\n {path_psf_2}\n')
        psf_1 = fits.getdata(path_psf_1); psf_2 = fits.getdata(path_psf_2)
        if display: print(f' [INFO] np.shape(psf1) = {np.shape(psf_1)} \n [INFO] np.shape(psf2) = {np.shape(psf_2)} ')
        psf = np.concatenate((psf_1, psf_2))
        if display: print(f' [INFO] np.shape(psf) = {np.shape(psf)} # after concatenation of PSF 1 and PSF 2')
        psf = np.nansum(psf, axis=0)
        if display: print(f' [INFO] np.shape(psf) = {np.shape(psf)} # after summing the PSF')
    
    else:
        path_psf = os.path.join(DATADIR + FN_PSF)
        if display: print(f'The path for the PSF data:\n {path_psf}\n')
        psf = fits.getdata(path_psf)
    
    if SPECTRAL_AXIS: 
        if display:
            print('Consider the spectral channels of interest:')
            if len(np.shape(psf)) == 4: print(f' [INFO] the axis of psf are wavelength, temporal, y, x.')
            elif len(np.shape(psf)) == 3: print(f' [INFO] the axis of psf are wavelength, y, x.')
            if display: print(f' [INFO] np.shape(psf) = {np.shape(psf)} # before selecting the spectral channels')
        psf = psf[CHANNELS] # keep the relevant spectral channels, written in CHANNELS (which is a int or a list of int)
        if display: print(f' [INFO] np.shape(psf) = {np.shape(psf)} # after selecting the spectral channels')
        if CHANNELS_COMBINED:
            psf = np.nansum(psf, axis=0) # sum channels (if CHANNELS_COMBINED set to True), otherwise consider one channel
            if display: print(f' [INFO] np.shape(psf) = {np.shape(psf)} # after summing the spectral channels')
        if len(np.shape(psf)) == 3: 
            psf = np.nansum(psf, axis=0) # sum the PSF on the temporal axis.
            if display: print(f' [INFO] np.shape(psf) = {np.shape(psf)} # after summing along the temporal axis')

    if SPATIAL_SHIFT_PSF_DATA: psf = vip.preproc.recentering.frame_shift(psf,SPATIAL_SHIFT_PSF_DATA,SPATIAL_SHIFT_PSF_DATA) 

    if CROP_PSF !=0: # crop the PSF
        if display: print(f'Crop the PSF: \n [INFO] The size of the PSF data *before* cropping is {np.shape(psf)}.')
        psf = psf[CROP_PSF:-CROP_PSF+1, CROP_PSF:-CROP_PSF+1]
        if display: print(f' [INFO] The size of the PSF data *after* cropping is {np.shape(psf)}.')
    else:
        if display: print(f'The size of the PSF data is: {np.shape(psf)}')
    
    # Normalize the PSF. The sum of the PSF should be equal to 1
    total_flux_psf = np.nansum(psf)
    if display: print(f'The total flux of the PSF image is {total_flux_psf}.')
    psf = psf/total_flux_psf

    if WRITETO: fits.writeto(os.path.join(inputs_resultdir,f'PSF{ID}.fits'), psf, overwrite=True)
    
    return psf


def load_PSF_one_or_several_datasets(dico = None, WRITETO=True):
    '''
    Return the normalized PSF of the dataset, or the different datasets considered.
    Use the function load_one_PSF().
    '''
    # Access extra variables from dico
    display      = dico.get('display', 0)
    NB_OBS       = dico.get('nb_obs', 'PROBLEM')
    DATADIR_ALL  = dico.get('datadir_all', 'PROBLEM')
    FN_PSF_ALL   = dico.get('fn_psf_all', 'PROBLEM')
    TWO_PSF_FILES_ALL = dico.get('two_psf_files_all', 'PROBLEM') # indicate whether there are two different files to consider for the PSF (1 = yes, 0 = no)
    FN_PSF_1_ALL = dico.get('fn_psf_1_all', 'PROBLEM')
    FN_PSF_2_ALL = dico.get('fn_psf_2_all', 'PROBLEM')
    CROP_PSF_ALL = dico.get('crop_psf_all', 'PROBLEM')
    SPATIAL_SHIFT_PSF_DATA_ALL = dico.get('spatial_shift_psf_data_all','PROBLEM')
    SPECTRAL_AXIS_ALL = dico.get('spectral_axis_all', 'PROBLEM')
    CHANNELS_ALL      = dico.get('channels_all', 'PROBLEM')
    inputs_resultdir      = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if NB_OBS == 'PROBLEM': raise ValueError('There is a problem with the value of NB_OBS.')
    if type(SPATIAL_SHIFT_PSF_DATA_ALL) == type(''): raise ValueError('There is a problem with the value of SPATIAL_SHIFT_PSF_DATA.')
    if type(TWO_PSF_FILES_ALL) == type(''): raise ValueError('There is a problem with the value of CROP_PSF.')
    if type(SPECTRAL_AXIS_ALL) == type('PROBLEM'): raise ValueError('There is a problem with the value of SPECTRAL_AXIS_ALL.')
    if type(CHANNELS_ALL)      == type('PROBLEM'): raise ValueError('There is a problem with the value of CHANNELS_ALL.')

    if WRITETO :
        if inputs_resultdir == 'PROBLEM': raise ValueError('There is a problem with the value of inputs_resultdir.')
        
    if NB_OBS == 1: # only one dataset
        dico['datadir']  = DATADIR_ALL[0]
        dico['fn_psf']   = FN_PSF_ALL[0]
        dico['fn_psf_1'] = FN_PSF_1_ALL[0]
        dico['fn_psf_2'] = FN_PSF_2_ALL[0]
        dico['crop_psf'] = CROP_PSF_ALL[0]
        dico['spectral_axis']     = SPECTRAL_AXIS_ALL[0]
        dico['channels']          = CHANNELS_ALL[0]
        dico['two_psf_files']     = TWO_PSF_FILES_ALL[0]
        dico['spatial_shift_psf_data'] = SPATIAL_SHIFT_PSF_DATA_ALL[0]
        psf = [load_PSF_one_dataset(dico=dico, ID='',WRITETO=WRITETO)]
        
    else:
        psf = []
        for i in range(NB_OBS): # loop other the different datasets
            dico['datadir']  = DATADIR_ALL[i]
            dico['fn_psf']   = FN_PSF_ALL[i]
            dico['fn_psf_1'] = FN_PSF_1_ALL[i]
            dico['fn_psf_2'] = FN_PSF_2_ALL[i]
            dico['crop_psf'] = CROP_PSF_ALL[i]
            dico['spectral_axis']     = SPECTRAL_AXIS_ALL[i]
            dico['channels']          = CHANNELS_ALL[i]
            dico['two_psf_files']     = TWO_PSF_FILES_ALL[i]
            dico['spatial_shift_psf_data'] = SPATIAL_SHIFT_PSF_DATA_ALL[i]
    
            psf.append( load_PSF_one_dataset(dico=dico, ID=f'_{i}', WRITETO=WRITETO) )

    return np.array(psf)


def load_SCIENCE_one_dataset(dico = None, WRITETO=True, ID=''):
    '''
    Return the science data of the dataset. 
    This function differs if the data are acquired in polarised light or total intensity light.
    Save the science data in the path 'inputs_resultdir'.
    
    Note: assume the following global variables to be defined before calling this function
    .DATA_DIR (string): common prefix path
    .PRE_PROCESS (string): folder in which is located the PSF (for total intensity data)
    .POST_PROCESS (string): folder in which is located the PSF (for polar data)
    .params_yaml (yaml file): configuration file in which some parameters should be defined (FN_SCIENCE)
    .IBAND (int): index of the band to consider
    .CROP_SCIENCE (int): cropping value apply to the left, right, top, and bottom of the image
    .display (boolean): whether to display information 
    .inputs_resultdir (string): path where to save the files
    '''
    print('\n(Load the SCIENCE_DATA)')

    # Access extra variables from dico
    display    = dico.get('display', 0)
    DATADIR    = dico.get('datadir', 'PROBLEM')
    FN_SCIENCE = dico.get('fn_science', 'PROBLEM')
    CROP_SCIENCE  = dico.get('crop_science', 'PROBLEM')
    SPECTRAL_AXIS = dico.get('spectral_axis', None)
    CHANNELS   = dico.get('channels', None)
    CHANNELS_COMBINED = bool(np.where(len(CHANNELS) > 1, True, False))
    inputs_resultdir  = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if DATADIR == 'PROBLEM': raise ValueError('There is a problem with the value of DATADIR.')
    if type(CROP_SCIENCE) == type(''): raise ValueError('There is a problem with the value of CROP_SCIENCE.')
    if type(CHANNELS) == type('PROBLEM'): raise ValueError('There is a problem with the value of CHANNELS.')
     
    if WRITETO :
        if inputs_resultdir == 'PROBLEM': raise ValueError('There is a problem with the value of inputs_resultdir.')
    
    path_science = os.path.join(DATADIR, FN_SCIENCE)
    if display: print(f'The path for the SCIENCE data:\n {path_science}\n')
    science_data = fits.getdata(path_science)

    if SPECTRAL_AXIS: # there is a spectral axis
        if display: 
            print('Consider the spectral channels of interest:')
            if len(np.shape(science_data)) == 4: print(f' [INFO] The axis of SCIENCE_DATA are wavelength, temporal, y, x.')
            elif len(np.shape(science_data)) == 3: print(f' [INFO] The axis of SCIENCE_DATA are wavelength, y, x.')
            print(f' [INFO] np.shape(science_data) = {np.shape(science_data)} # before selecting the spectral channels')
        science_data = science_data[CHANNELS] # consider the relevant spectral channels
        if display:print(f' [INFO] np.shape(science_data) = {np.shape(science_data)} # after selecting the spectral channels')
        if CHANNELS_COMBINED: 
            science_data = np.nansum(science_data, axis=0)
            if display: print(f' [INFO] np.shape(science_data) = {np.shape(science_data)} # after combining the spectral channels')

    if WRITETO: fits.writeto(os.path.join(inputs_resultdir, f'science_cube{ID}.fits'), science_data, overwrite=True)
    
   
    # Crop the spatial dimensions
    if  CROP_SCIENCE != 0:
        if display: print(f'Crop the SCIENCE_DATA: \n [INFO] The size of the SCIENCE_DATA *before* cropping is {np.shape(science_data)}.')
        if len(np.shape(science_data)) == 2: science_data = science_data[CROP_SCIENCE:-CROP_SCIENCE, CROP_SCIENCE:-CROP_SCIENCE]
        elif len(np.shape(science_data)) == 3: science_data = science_data[:,CROP_SCIENCE:-CROP_SCIENCE, CROP_SCIENCE:-CROP_SCIENCE]
        else: raise ValueError(f'[ERROR] The dimension of the SCIENCE_DATA is weird, it should be 2 or 3 but is {len(np.shape(science_data))}, check why!')
        if display: print(f' [INFO] The size of the SCIENCE_DATA *after* cropping is {np.shape(science_data)}.')

    elif CROP_SCIENCE == 0 and display: print(f' [INFO] The size of the SCIENCE_DATA is {np.shape(science_data)}.')

    if WRITETO and len(np.shape(science_data)) == 2: fits.writeto(os.path.join(inputs_resultdir,f'science_data{ID}.fits'), science_data, overwrite=True) # save the science data only if it has a dimension equal to 2,  to avoid saving heavy files. This file is not necessarily, but can be useful to check if the script raises some errors

    return np.array(science_data)


def load_SCIENCE_one_or_several_datasets(dico = None, WRITETO=True):
    '''
    Return the SCIENCE data of the dataset, or the different datasets considered.
    Use the function load_one_SCIENCE().
    '''
    # Access extra variables from dico
    display = dico.get('display', 0)
    NB_OBS    = dico.get('nb_obs', 'PROBLEM')
    DATADIR_ALL       = dico.get('datadir_all', 'PROBLEM')
    FN_SCIENCE_ALL    = dico.get('fn_science_all', 'PROBLEM')
    CROP_SCIENCE_ALL  = dico.get('crop_science_all', 'PROBLEM')
    SPECTRAL_AXIS_ALL = dico.get('spectral_axis_all', None)
    CHANNELS_ALL      = dico.get('channels_all', None)
    inputs_resultdir  = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if NB_OBS == 'PROBLEM': raise ValueError('There is a problem with the value of NB_OBS.')

    if NB_OBS == 1: # only one dataset
        dico['fn_science'] = FN_SCIENCE_ALL[0]
        dico['crop_science'] = CROP_SCIENCE_ALL[0]
        dico['spectral_axis'] = SPECTRAL_AXIS_ALL[0]
        dico['channels'] = CHANNELS_ALL[0]

        science_data = [load_SCIENCE_one_dataset(dico=dico, ID='', WRITETO=WRITETO)]
        
    else:
        science_data = []
        for i in range(NB_OBS): # loop other the different datasets
            dico['datadir'] = DATADIR_ALL[i]
            dico['fn_science'] = FN_SCIENCE_ALL[i]
            dico['crop_science'] = CROP_SCIENCE_ALL[i]
            dico['spectral_axis'] = SPECTRAL_AXIS_ALL[i]
            dico['channels'] = CHANNELS_ALL[i]

            science_data.append( load_SCIENCE_one_dataset(dico=dico, ID=f'_{i}', WRITETO=WRITETO) )

    return science_data


def load_NOISE_one_dataset(dico = None, WRITETO=True, ID=''):
    '''
    Return the noise map of the dataset. 
    This function differs if the data are acquired in polarised light or total intensity light.
    Save the noise map file in the path 'inputs_resultdir'.
    
    Note: assume the following global variables to be defined before calling this function
    .DATA_DIR (string): common prefix path
    .PRE_PROCESS (string): folder in which is located the PSF (for total intensity data)
    .POST_PROCESS (string): folder in which is located the PSF (for polar data)
    .params_yaml (yaml file): configuration file in which some parameters should be defined (FN_NOISE, or METH_NOISE)
    .CROP_NOISE (int): cropping value apply to the left, right, top, and bottom of the image
    .display (boolean): whether to display information 
    .inputs_resultdir (string): path where to save the files

    (optional -  only need to be defined if TYPE_OBS set to 'total_intensity' and METH_NOISE set to 'compute_it', as
    in this case the NOISE map should be derived based on the SCIENCE_DATA cube processed by PCA with opposite parallactic angles.)
    .SCIENCE_DATA (2D array if TYPE_OBS = polar, 3D array if TYPE_OBS = total_intensity): 
    .PA_ARRAY (1D array): parallactic angles
    .NMODES (int): number of modes/components to use when applying PCA 
    .IWA (int): radius of the mask corresponding approximately to the inner working angle of the coronagraph
    '''
    print('\n(Load the NOISE_MAP)')
    # Access extra variables from dico
    display    = dico.get('display', 0)
    DATADIR    = dico.get('datadir', 'PROBLEM')
    FN_NOISE   = dico.get('fn_noise', 'PROBLEM')
    CROP_NOISE = dico.get('crop_noise', 'PROBLEM')
    SPECTRAL_AXIS = dico.get('spectral_axis', None)
    CHANNELS   = dico.get('channels', None)
    CHANNELS_COMBINED = bool(np.where(len(CHANNELS) > 1, True, False)) 
    IWA    = dico.get('iwa', 7)
    NMODES = dico.get('nmodes', 10)
    SCIENCE_DATA = dico.get('science_data','PROBLEM')
    PA_ARRAY     = dico.get('pa_array','PROBLEM')
    NOISE_MULTIPLICATION_FACTOR = dico.get('noise_multiplication_factor', 'PROBLEM')
    COMPUTE_NOISE_MAP = dico.get('compute_noise_map', 'PROBLEM')
    inputs_resultdir  = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if DATADIR == 'PROBLEM': raise ValueError('There is a problem with the value of DATADIR.')
    if type(CROP_NOISE) == type(''): raise ValueError('There is a problem with the value of CROP_NOISE.')
    if type(COMPUTE_NOISE_MAP) == type(''): raise ValueError('There is a problem with the value of COMPUTE_NOISE_MAP.')
    if NOISE_MULTIPLICATION_FACTOR == 'PROBLEM': raise ValueError('There is a problem with the value of NOISE_MULTIPLICATION_FACTOR.') 
    if WRITETO :
        if inputs_resultdir == 'PROBLEM': raise ValueError('There is a problem with the value of inputs_resultdir.')

    # Load the noise map or...
    if not COMPUTE_NOISE_MAP: 
        path_noise = os.path.join(DATADIR, FN_NOISE)
        if display: print(f'The path for the NOISE data:\n {path_noise}\n')
        noise_map = fits.getdata(path_noise)

        if SPECTRAL_AXIS: # there is a spectral axis. Assumption: the noise map (so maybe not a 2D map yet) have the same dimension that the SCIENCE data indicated in the configuration file (and so before going through the functions load_SCIENCE_several_datasets, load_SCIENCE_one_dataset )
            if display: 
                print('Consider the spectral channels of interest:')
                if len(np.shape(noise_map)) == 4: print(f' [INFO] The axis of NOISE_MAP are wavelength, temporal, y, x.')
                elif len(np.shape(noise_map)) == 3: print(f' [INFO] The axis of NOISE_MAP are wavelength, y, x.')
                print(f' [INFO] np.shape(noise_map) = {np.shape(noise_map)} # before selecting the spectral channels')
            noise_map = noise_map[CHANNELS] # consider the relevant spectral channels
            if display: print(f' [INFO] np.shape(noise_map) = {np.shape(noise_map)} # after selecting the spectral channels')
            if CHANNELS_COMBINED: 
                noise_map = np.nansum(noise_map, axis=0)
                if display: print(f' [INFO] np.shape(noise_map) = {np.shape(noise_map)} # after combining the spectral channels')

    # ... compute it 
    else:
        # Check the required input parameters have been given
        if type(SCIENCE_DATA) == type(''): raise ValueError('There is a problem with the value of SCIENCE_DATA.')
        if type(IWA) == type(''): raise ValueError('There is a problem with the value of MASK_RAD.')
        if type(NMODES) == type(''): raise ValueError('There is a problem with the value of NMODES.')
        if type(PA_ARRAY) == type(''): raise ValueError('There is a problem with the value of PA_ARRAY.')
    
        print(f'The NOISE_MAP is computed by processing the SCIENCE_DATA with PCA using the minus parallactic angles and {NMODES} nmodes.')
        noise_almost = vip.psfsub.pca_fullfr.pca(SCIENCE_DATA, -PA_ARRAY, ncomp=NMODES, mask_center_px=IWA, imlib='opencv', full_output=False, verbose=False)
        
        if WRITETO: fits.writeto(os.path.join(inputs_resultdir,f'reduced_image_opp_pa{ID}.fits'), noise_almost, overwrite=True)
        noise_map = compute_limdet_map_ann(noise_almost, dr=2, alpha=1, center='center', even_or_odd='even')

    noise_map[noise_map==0] = np.nan # later in the script, the noise_map will be used to divide something, so prevent any potential division per 0

    if CROP_NOISE != 0:
        if display: print(f'Crop the noise map: \n [INFO] The size of the NOISE_MAP *before* cropping is {np.shape(noise_map)}.')
        noise_map = noise_map[CROP_NOISE:-CROP_NOISE, CROP_NOISE:-CROP_NOISE]
        if display: print(f' [INFO] The size of the NOISE_MAP *after* cropping is {np.shape(noise_map)}.')
    elif CROP_NOISE == 0 and display: print(f'The size of the NOISE_MAP is {np.shape(noise_map)}.')

    if NOISE_MULTIPLICATION_FACTOR != 1. : 
        if display: print(f'Multiply the NOISE_MAP by {NOISE_MULTIPLICATION_FACTOR}.') 
    if WRITETO: 
        print('Save the NOISE_MAP.')
        fits.writeto(os.path.join(inputs_resultdir,f'NOISE_MAP{ID}.fits'), noise_map, overwrite=True)
        if WRITETO and len(np.shape(SCIENCE_DATA)) == 2: fits.writeto(os.path.join(inputs_resultdir,f'science_data_snr{ID}.fits'), SCIENCE_DATA/noise_map, overwrite=True) # save the S/N map of the SCIENCE_DATA only if it has a dimension equal to 2, to avoid saving heavy files. This file is not necessarily, but can be useful to check if the script raises some errors
    return  np.array(noise_map)


def load_NOISE_one_or_several_datasets(dico = None, WRITETO=True):
    '''
    Return the NOISE data of the dataset, or the different datasets considered.
    Use the function load_one_NOISE().
    '''
    # Access extra variables from dico
    display = dico.get('display', 0)
    NB_OBS    = dico.get('nb_obs', 'PROBLEM')
    DATADIR_ALL       = dico.get('datadir_all', 'PROBLEM')
    SCIENCE_DATA_ALL  = dico.get('science_data_all', 'PROBLEM')
    PA_ARRAY_ALL      = dico.get('pa_array_all', 'PROBLEM')
    FN_NOISE_ALL      = dico.get('fn_noise_all', 'PROBLEM')
    CROP_NOISE_ALL    = dico.get('crop_noise_all', 'PROBLEM')
    SPECTRAL_AXIS_ALL = dico.get('spectral_axis_all', None)
    CHANNELS_ALL      = dico.get('channels_all', 'PROBLEM')
    COMPUTE_NOISE_MAP_ALL = dico.get('compute_noise_map_all', 'PROBLEM')
    NOISE_MULTIPLICATION_FACTOR_ALL = dico.get('noise_multiplication_factor_all', 'PROBLEM')

    IWA_ALL =  dico.get('iwa_all', 'PROBLEM')
    inputs_resultdir = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if NB_OBS == 'PROBLEM': raise ValueError(f'There is a problem with the value of NB_OBS which is {NB_OBS}.')
    if type(CROP_NOISE_ALL) == type(''): raise ValueError(f'There is a problem with the value of CROP_NOISE_ALL which is {CROP_NOISE_ALL}.')
    if type(COMPUTE_NOISE_MAP_ALL) == type(''): raise ValueError(f'There is a problem with the value of COMPUTE_NOISE_MAP_ALL which is {COMPUTE_NOISE_MAP_ALL}.')
    if type(NOISE_MULTIPLICATION_FACTOR_ALL) == 'PROBLEM': raise ValueError(f'There is a problem with the value of NOISE_MULTIPLICATION_FACTOR_ALL which is {NOISE_MULTIPLICATION_FACTOR_ALL}.')
    if type(SPECTRAL_AXIS_ALL) == type('PROBLEM'): raise ValueError(f'There is a problem with the value of SPECTRAL_AXIS_ALL which is {SPECTRAL_AXIS_ALL}.')
    if type(CHANNELS_ALL)      == type('PROBLEM'): raise ValueError(f'There is a problem with the value of CHANNELS_ALL which is {CHANNELS_ALL}.')
    if WRITETO :
        if inputs_resultdir == 'PROBLEM': raise ValueError(f'There is a problem with the value of inputs_resultdir which is {inputs_resultdir}.')


    if NB_OBS == 1: # only one dataset
        dico['datadir']       = DATADIR_ALL[0]
        dico['fn_noise']      = FN_NOISE_ALL[0]
        dico['crop_noise']    = CROP_NOISE_ALL[0]
        dico['science_data']  = SCIENCE_DATA_ALL[0]
        dico['pa_array']      = PA_ARRAY_ALL[0]
        dico['iwa']           = IWA_ALL[0]
        dico['spectral_axis'] = SPECTRAL_AXIS_ALL[0]
        dico['channels']      = CHANNELS_ALL[0]
        dico['compute_noise_map'] = COMPUTE_NOISE_MAP_ALL[0]
        dico['noise_multiplication_factor'] = NOISE_MULTIPLICATION_FACTOR_ALL[0]

        noise_map = [load_NOISE_one_dataset(dico, ID='', WRITETO=WRITETO)]
        
    else:
        noise_map = []
        for i in range(NB_OBS): # loop other the different datasets
            dico['datadir']       = DATADIR_ALL[i]
            dico['fn_noise']      = FN_NOISE_ALL[i]
            dico['crop_noise']    = CROP_NOISE_ALL[i]
            dico['science_data']  = SCIENCE_DATA_ALL[i]
            dico['pa_array']      = PA_ARRAY_ALL[i]
            dico['iwa']           = IWA_ALL[i]
            dico['spectral_axis'] = SPECTRAL_AXIS_ALL[i]
            dico['channels']      = CHANNELS_ALL[i]
            dico['compute_noise_map'] = COMPUTE_NOISE_MAP_ALL[i]
            dico['noise_multiplication_factor'] = NOISE_MULTIPLICATION_FACTOR_ALL[i]

            noise_map.append( load_NOISE_one_dataset(dico, ID=f'_{i}', WRITETO=WRITETO ) )

    return noise_map
       

def load_PA_ARRAY_one_dataset(dico = None, ID='', WRITETO=False):
    '''
    Return the parallactic angles array for pupil-tracking observations (assumed to be acquired in 'total_intensity' and not 'polar' light).
    Otherwise, return None.
    Save the parallactic angles file in the path 'inputs_resultdir'.
    
    Note: assume the following global variables to be defined before calling this function
    .TYPE_OBS (string): set to 'polar' or 'total_intensity' depending on the data
    .DATA_DIR (string): common prefix path
    .PRE_PROCESS (string): folder in which is located the PSF (for total intensity data)
    .params_yaml (yaml file): configuration file in which some parameters should be defined (FN_PA)
    .display (boolean): whether to display information 
    .inputs_resultdir (string): path where to save the files
    '''
    print('\n(Load the PA - PARALLACTIC ANGLES - array)')
    # Access extra variables from dico
    display  = dico.get('display', 0)
    TYPE_OBS = dico.get('type_obs', 'PROBLEM')
    FN_PA    = dico.get('fn_pa', 'PROBLEM')
    DATADIR  = dico.get('datadir', 'PROBLEM')

    if TYPE_OBS == 'PROBLEM': raise ValueError('There is a problem with the value of TYPE_OBS.')
    if DATADIR  == 'PROBLEM': raise ValueError('There is a problem with the value of DATADIR.')
        
    if TYPE_OBS == 'total_intensity':
        path_pa  = os.path.join(DATADIR, FN_PA)
        if display: print(f'The path for the parallactic angles array:\n {path_pa}\n')
        pa_array = -fits.getdata(path_pa)
        if display: print(f'The shape of the parallactic angles array is {np.shape(pa_array)}.')
        return np.array(pa_array)
    else:
        return None


def load_PA_ARRAY_one_or_several_datasets(dico = None, WRITETO=False):
    '''
    Return the parallactic angles array for one or several pupil-tracking observations.
    Use the function load_one_PA_ARRAY().
    '''
    # Access extra variables from dico
    display = dico.get('display', 0)
    NB_OBS    = dico.get('nb_obs', 'PROBLEM')
    TYPE_OBS_ALL = dico.get('type_obs_all', 'PROBLEM')
    DATADIR_ALL  = dico.get('datadir_all', 'PROBLEM')
    FN_PA_ALL    = dico.get('fn_pa_all', 'PROBLEM')

    if NB_OBS == 1: # only one dataset
        dico['type_obs'] = TYPE_OBS_ALL[0]
        dico['datadir']  = DATADIR_ALL[0]
        dico['fn_pa']    = FN_PA_ALL[0]
        pa_array = [load_PA_ARRAY_one_dataset(dico=dico, ID=f'')]
        
    else:
        pa_array = []
        for i in range(NB_OBS): # loop other the different datasets
            dico['type_obs'] = TYPE_OBS_ALL[i]
            dico['datadir']  = DATADIR_ALL[i]
            dico['fn_pa']    = FN_PA_ALL[i]
            pa_array.append( load_PA_ARRAY_one_dataset(dico=dico, ID=f'_{i}') )

    return pa_array


def load_MASK2MINIMIZE_one_dataset(dico = None, WRITETO = True, ID=''):
    '''
    Return the region where the disk model should match the SCIENCE_DATA. 
    This function differs if the data are acquired in polarised light or total intensity light.
    Save the mask map in the path 'inputs_resultdir'.
    
    Note: assume the following global variables to be defined before calling this function
    .display (boolean): whether to display information 
    .inputs_resultdir (string): path where to save the files

    '''
    print('\n(Load the MASK2MINIMIZE map) \n Remark: The MASK2MINIMIZE map define the region where the disk model will be optimized to match the SCIENCE_DATA, after SCIENCE_DATA have been processed.')
    # Access extra variables from dico
    display   = dico.get('display', 0)
    PATH_MASK = dico.get('path_mask', 'PROBLEM') # the full path is already given because the mask used could be located somewhere than the science/psf(/noise/pa_angles) data
    CROP_MASK = dico.get('crop_mask', 'PROBLEM')
    inputs_resultdir = dico.get('inputs_resultdir', 'PROBLEM')
    #WRITETO = False

    # Check if some extra keyword arguments were effectively given
    if type(CROP_MASK) == type('PROBLEM'): raise ValueError('There is a problem with the value of CROP_MASK.')
    if WRITETO :
        if inputs_resultdir == 'PROBLEM': raise ValueError('There is a problem with the value of inputs_resultdir.')
    if display: print(f'The path for the MASK is\n {PATH_MASK}\n')

    if PATH_MASK[-4:] == 'fits': mask2minimize = fits.getdata(PATH_MASK)

    else: raise ValueError(f' [ERROR] The extension of the MASK2MINIMIZE file should be .fits and here the path to the file is \n{PATH_MASK}\n')

    if CROP_MASK != 0: # Crop the mask
        if display: print(f'Crop spatial dimensions of MASK2MINIMIZE: \n [INFO] The shape of the MASK2MINIMIZE data *before* cropping is {np.shape(mask2minimize)}.')
        mask2minimize = mask2minimize[CROP_MASK:-CROP_MASK, CROP_MASK:-CROP_MASK]
        if display: print(f' [INFO] The shape of the MASK2MINIMIZE data *after* cropping is {np.shape(mask2minimize)}.')

    elif CROP_MASK == 0 and display: print(f'The shape of the MASK2MINIMIZE is {np.shape(mask2minimize)}.')
    
    if WRITETO: fits.writeto(os.path.join(inputs_resultdir,f'MASK2MINIMIZE{ID}.fits'), mask2minimize, overwrite=True)
    return mask2minimize



def load_MASK2MINIMIZE_one_or_several_datasets(dico = None, WRITETO = True):
    '''
    Return the region where the disk model should match the SCIENCE_DATA. 
    This function differs if the data are acquired in polarised light or total intensity light.
    Save the mask map in the path 'inputs_resultdir'.
    
    Note: assume the following global variables to be defined before calling this function
    .display (boolean): whether to display information 
    .inputs_resultdir (string): path where to save the files
    '''
    print('\n(Load MASK data)')
    # Access extra variables from dico
    display = dico.get('display', 0)
    NB_OBS = dico.get('nb_obs', 'PROBLEM')
    PATH_MASK_ALL = dico.get('path_mask_all', 'PROBLEM')
    CROP_MASK_ALL = dico.get('crop_mask_all', 'PROBLEM')
    inputs_resultdir = dico.get('inputs_resultdir', 'PROBLEM')
    #WRITETO = False

    if NB_OBS == 1: # only one dataset
        dico['path_mask'] = PATH_MASK_ALL[0]
        dico['crop_mask'] = CROP_MASK_ALL[0]

        mask2minimize = [load_MASK2MINIMIZE_one_dataset(dico, ID='', WRITETO=WRITETO)]
        
    else:
        mask2minimize = []
        for i in range(NB_OBS): # loop other the different datasets
            dico['path_mask'] = PATH_MASK_ALL[i]
            dico['crop_mask'] = CROP_MASK_ALL[i]
            mask2minimize.append( load_MASK2MINIMIZE_one_dataset(dico, ID=f'_{i}', WRITETO=WRITETO ) )

    return mask2minimize




## PROCESS DATA ##
def process_SCIENCE_PCA_one_dataset(dico = None, WRITETO=False, ID=''):
    '''
    Return the PCA-reduced data for pupil-tracking observations (assumed to be acquired in 'total_intensity' and not 'polar' light).
    Otherwise, return None.
    Save at the path 'inputs_resultdir' the reduced data in different flavours: only the image, the image masked, or the cube rotating at the different parallactic angles.
    
    Note: assume the following global variables to be defined before calling this function
    .TYPE_OBS (string): set to 'polar' or 'total_intensity' depending on the data
    .SCIENCE_DATA (2D array if TYPE_OBS = polar, 3D array if TYPE_OBS = total_intensity): 
    .PA_ARRAY (1D array): parallactic angles
    .NMODES (int): number of modes/components to use when applying PCA 
    .MASK_RAD (int): radius of the mask corresponding approximately to the inner working angle of the coronagraph
    .MASK2MINIMIZE (2D array): region where the disk model should match the SCIENCE_DATA. 
    .display (boolean): whether to display information 
    .inputs_resultdir (string): path where to save the files
    '''
    # Access extra variables from dico
    params_yaml = dico.get('params_yaml', None)
    display  = dico.get('display', 0)
    TYPE_OBS = dico.get('type_obs', 'PROBLEM')
    IWA      = dico.get('iwa', 7)
    NMODES   = dico.get('nmodes', 10)
    SCIENCE_DATA  = dico.get('science_data','PROBLEM')
    MASK2MINIMIZE = dico.get('mask2minimize', 'PROBLEM')
    PA_ARRAY      = dico.get('pa_array', 'PROBLEM')
    inputs_resultdir = dico.get('inputs_resultdir', 'PROBLEM')

    if TYPE_OBS == 'total_intensity':
        print('\n(Process the SCIENCE data)')
        print('We reduced the data by applying PCA.')
        red_data =  vip.psfsub.pca_fullfr.pca(np.copy(SCIENCE_DATA), PA_ARRAY, ncomp=NMODES, mask_center_px=IWA, imlib='opencv', full_output=False, verbose=False)

        if WRITETO:
            fits.writeto(os.path.join(inputs_resultdir,f'reduced_image{ID}.fits'), red_data, overwrite=True)
            fits.writeto(os.path.join(inputs_resultdir,f'reduced_image_mask{ID}.fits'), red_data*MASK2MINIMIZE, overwrite=True)
        return red_data
    return None

## PROCESS DATA ##
def process_SCIENCE_PCA_several_datasets(dico = None, WRITETO=False):
    '''
    Return the PCA-reduced data for pupil-tracking observation(s).
    Use the function process_one_SCIENCE_PCA().
    '''
    # Access extra variables from dico
    display = dico.get('display', 0)
    NB_OBS    = dico.get('nb_obs', 'PROBLEM')
    TYPE_OBS_ALL = dico.get('type_obs_all', 'PROBLEM')
    DATADIR_ALL  = dico.get('datadir_all', 'PROBLEM')
    IWA_ALL      = dico.get('iwa_all', 7)
    NMODES_ALL   = dico.get('nmodes_all', 10)
    SCIENCE_DATA_ALL  = dico.get('science_data_all','PROBLEM')
    MASK2MINIMIZE_ALL = dico.get('mask2minimize_all', 'PROBLEM')
    PA_ARRAY_ALL      = dico.get('pa_array_all', 'PROBLEM')
    inputs_resultdir  = dico.get('inputs_resultdir', 'PROBLEM')

    if NB_OBS == 1: # only one dataset
        dico['science_data']  = SCIENCE_DATA_ALL[0]
        dico['mask2minimize'] = MASK2MINIMIZE_ALL[0]
        dico['type_obs'] = TYPE_OBS_ALL[0]
        dico['pa_array'] = PA_ARRAY_ALL[0]
        dico['nmodes']   = NMODES_ALL[0]
        dico['iwa']      = IWA_ALL[0]
        red_data = [process_SCIENCE_PCA_one_dataset(dico=dico, ID='', WRITETO=WRITETO)]
        
    else:
        red_data = []
        for i in range(NB_OBS): # loop other the different datasets
            dico['science_data']  = np.array(SCIENCE_DATA_ALL[i])
            dico['mask2minimize'] = np.array(MASK2MINIMIZE_ALL[i])
            dico['type_obs'] = TYPE_OBS_ALL[i]
            dico['pa_array'] = PA_ARRAY_ALL[i]
            dico['nmodes']   = NMODES_ALL[i]
            dico['iwa']      = IWA_ALL[i]
            red_data.append( process_SCIENCE_PCA_one_dataset(dico=dico, ID=f'_{i}', WRITETO=WRITETO) ) 

    return red_data
        
    
def apply_MASK2SCIENCE_one_dataset(dico = None, WRITETO=False):
    '''
    Return the science data masked if not in the region of interest. The region of interest is  where the disk model should match the science data.

   # Save at the path 'inputs_resultdir' the masked science data.
    
    Note: assume the following global variables to be defined before calling this function
    .TYPE_OBS (string): set to 'polar' or 'total_intensity' depending on the data
    .SCIENCE_DATA (2D array if TYPE_OBS = polar, 3D array if TYPE_OBS = total_intensity):
    .MASK2MINIMIZE (2D array): region where the disk model should match the SCIENCE_DATA.
    .inputs_resultdir (string): path where to save the files
    
    if TYPE_obs = total_intensity
    .PA_ARRAY (1D array): parallactic angles
    '''
    print('\n(Apply the MASK to the SCIENCE data)')
    # Access extra variables from dico
    params_yaml = dico.get('params_yaml', None)
    display = dico.get('display', 0)
    TYPE_OBS = dico.get('type_obs', 'PROBLEM')
    SCIENCE_DATA = dico.get('science_data', 'PROBLEM')
    PA_ARRAY = dico.get('pa_array', 'PROBLEM')
    MASK2MINIMIZE = dico.get('mask2minimize', 'PROBLEM')
    inputs_resultdir = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if TYPE_OBS == 'PROBLEM': raise ValueError('There is a problem with the value of TYPE_OBS.')
    if type(SCIENCE_DATA) == type('PROBLEM'): raise ValueError('There is a problem with the value of SCIENCE_DATA.')
    if type(MASK2MINIMIZE) == type('PROBLEM'): raise ValueError('There is a problem with the value of MASK2MINIMIZE.')
    if WRITETO :
        if inputs_resultdir == 'PROBLEM': raise ValueError('There is a problem with the value of inputs_resultdir.')
       
    if TYPE_OBS == 'polar':
        science_data_mask = np.copy(SCIENCE_DATA) * MASK2MINIMIZE
        if WRITETO: fits.writeto(os.path.join(inputs_resultdir,'reduced_image_mask.fits'), science_data_mask, overwrite=True)
        
    elif TYPE_OBS == 'total_intensity':
        mask2minimize_cube = np.repeat(MASK2MINIMIZE[np.newaxis, :, :], len(PA_ARRAY), axis=0)
        mask2minimize_cube_pa = vip.preproc.derotation.cube_derotate(mask2minimize_cube, -PA_ARRAY, imlib='opencv', interpolation='nearneig')
        science_data_mask = np.copy(SCIENCE_DATA) * mask2minimize_cube_pa
        #fits.writeto(os.path.join(inputs_resultdir,'cube_mask_science.fits'), SCIENCE_DATA_MASK, overwrite=True)
        #fits.writeto(os.path.join(inputs_resultdir,'cube_mask.fits'), MASK2MINIMIZE_CUBE_PA, overwrite=True)
    return science_data_mask

def apply_MASK2SCIENCE_several_datasets(dico = None, WRITETO=False):
    '''
    Return the PCA-reduced data for pupil-tracking observation(s).
    Use the function process_one_SCIENCE_PCA().
    '''
    # Access extra variables from dico
    params_yaml = dico.get('params_yaml', None)
    display = dico.get('display', 0)
    TYPE_OBS_ALL = dico.get('type_obs_all', 'PROBLEM')
    NB_OBS = dico.get('nb_obs', 'PROBLEM')
    SCIENCE_DATA = dico.get('science_data', 'PROBLEM')
    PA_ARRAY = dico.get('pa_array', 'PROBLEM')
    MASK2MINIMIZE = dico.get('mask2minimize', 'PROBLEM')
    inputs_resultdir = dico.get('inputs_resultdir', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if TYPE_OBS_ALL == 'PROBLEM': raise ValueError('There is a problem with the value of TYPE_OBS.')
    if NB_OBS == 'PROBLEM': raise ValueError('There is a problem with the value of NB_OBS.')
    if type(SCIENCE_DATA) == type('PROBLEM'): raise ValueError('There is a problem with the value of SCIENCE_DATA.')
    if type(PA_ARRAY) == type('PROBLEM'): raise ValueError('There is a problem with the value of PA_ARRAY.')
    if type(MASK2MINIMIZE) == type('PROBLEM'): raise ValueError('There is a problem with the value of MASK2MINIMIZE.')
    if WRITETO :
        if inputs_resultdir == 'PROBLEM': raise ValueError('There is a problem with the value of inputs_resultdir.')
       
    if NB_OBS == 1: # only one dataset
        type_obs = TYPE_OBS_ALL
        pa = PA_ARRAY
        science =  SCIENCE_DATA
        dico['science_data'] = science
        dico['type_obs'] = type_obs
        dico['pa_array'] = pa
        science_data_mask = apply_MASK2SCIENCE_one_dataset(dico=dico, ID='', WRITETO=WRITETO)
        
    else:
        science_data_mask = []
        for i in range(NB_OBS): # loop other the different datasets
            type_obs = TYPE_OBS_ALL[i]
            pa = PA_ARRAY[i]
            science =  SCIENCE_DATA[i]
            dico['science_data'] = science
            dico['type_obs'] = type_obs
            dico['pa_array'] = pa
            science_data_mask.append( apply_MASK2SCIENCE_one_dataset(dico=dico, ID=f'_{i}', WRITETO=WRITETO) )

    return np.array(science_data_mask)