#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script with functions to fit via MCMC debris disks.

Functions:
    do_test_disk_empty()
    do_test_disk_first_guess()


This script would be imported by the scripts:
    diskfit_*params_*obs.py
'''

#from import_functions_generic import *

from derive_noise_map import *
from functions_MCMC import *
from packages import *

def do_test_disk_empty(PARAMS_INIT, dico = None):
    '''
    Return the value of the chisquare or logarithm of the likelihood (depending if the algorithm of exploration is AMOEBA or MCMC)
    for the absence of disk. This should be worst case scenario, as the disk model then should match the data, resulting in smaller residuals.
    
    Note: assume the following global variables to be defined before:
    .exploration_algo: algorithm of exploration (AMOEBA or MCMC)
    .THETA_INIT (1D array): initial model parameters
    '''

    display = dico.get('display', 0)

    if display: 
        print('\n=== Compute the likelihood and chisquare within the region to optimize (defined by MASK2MINIMIZE) *without* subtraction of any disk MODEL in the SCIENCE_DATA === \nRemark: Following disk simulations have to result in better likelihood and chisquare value than the ones computed here.')
        startTime =  datetime.now() 
    
    # Access extra keyword arguments from the dictionary
    
    PARAMS_NAMES = dico.get('params_names_unflat', 'PROBLEM')

    params_init_no_disk = copy.deepcopy(PARAMS_INIT)

    # Set the scaling parameter to 0. Loop on all the parameters to find it
    for i, params_names_struct_i in enumerate(PARAMS_NAMES):
        for j, param_name in enumerate(params_names_struct_i):
            if param_name[:len('SCALING')] == 'SCALING': 
                params_init_no_disk[i][j] = [0] * len(params_init_no_disk[i][j])

    if display: 
        #print(f'Check disk model parameters without flux (scaling_flux should be set to 0):\n')
        print_params_names_and_values(PARAMS_NAMES, params_init_no_disk, params_flat=False)
        print('Remark: The scaling parameter defining the flux of the disk should be equal to 0 here.')
    
    chisquare_init_nodisk = chisquare_params(params_init_no_disk, dico = dico,  params_flat=False)
    
    if display:  print(f"\nTime for a single model: {datetime.now() - startTime}")

    return chisquare_init_nodisk


def do_test_disk_first_guess(PARAMS_INIT, dico = None):
    '''
    Return the value of the chisquare or logarithm of the likelihood for the first guess of the algorithm of exploration (AMOEBA or MCMC).
    Save files (disk model, disk model convolved to the PSF, best residuals, best residuals normalized by the NOISE).
    
    Note: assume the following global variables to be defined before:
    .exploration_algo: algorithm of exploration (AMOEBA or MCMC)
    .THETA_INIT (1D array): initial model parameters
    .TYPE_OBS (string): observation type (polar or total_intensity)
    .PSF (2D array)
    .SCIENCE_DATA (2D array if TYPE_OBS = polar, 3D array if TYPE_OBS = total_intensity)
    .NOISE (2D array)
    .PA_ARRAY (if TYPE_OBS = total_intensity)
    .MASK2MINIMIZE (2D array): mask within the model should match the SCIENCE_DATA
    .firstguess_resultdir (string): path where to save the files
    '''
    display = dico.get('display', 0)
    
    if display: 
        print('\n === Compute the likelihood and chisquare for the first guess disk model ===\n')
        startTime =  datetime.now() 
    
    if display: 
        # Access extra keyword arguments from the dictionary    
        PARAMS_NAMES = dico.get('params_names_unflat', 'PROBLEM')

        print(f'Check the disk model parameters for the initial guess:')
        print_params_names_and_values(PARAMS_NAMES, PARAMS_INIT, params_flat=False)
    
    chisquare_init = chisquare_params(PARAMS_INIT, dico = dico,  params_flat=False)

    if display: print(f"\nTime for a single model: {datetime.now() - startTime}")

    return chisquare_init
    