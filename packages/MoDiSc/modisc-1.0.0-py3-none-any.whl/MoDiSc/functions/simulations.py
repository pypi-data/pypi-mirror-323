#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script with functions to fit via MCMC debris disks.

Functions:
    initialize_walkers_backend()
    from_param_to_theta_init() 
    from_param_to_theta_init_5params_1obs()
    from_param_to_theta_init_6params_1obs()
    from_param_to_theta_init_6params_2obs()
    from_param_to_theta_init_8params_2obs()
    logp()
    logl()
    logl_5params_1obs()
    logl_6params_1obs()
    logl_6params_2obs()
    logl_8params_2obs()
    lnpb_mcmc() # used when running the MCMC
    lnpb()
    generate_disk_model_5params()
    chisquare_params()
    chisquare_5params_1obs()
    chisquare_6params_1obs()
    chisquare_6params_2obs_polar()
    chisquare_8params_2obs_polar()


This script would be imported by the scripts:
    diskfit_*params_*obs.py
    plotfrombackend_*.py
    test_disks.py
'''

#from import_functions_generic import *
from packages import *
from derive_noise_map import *

def print_params_names_and_values(params_names, params_values, params_flat=True, skip_first_line=False):
    '''
    Print for each parameter its name and its value.
    '''

    if not skip_first_line: print(f'\nNames and values of the disk parameters:')
    
    if params_flat:
        for j_name, name in enumerate( params_names ):
            print(f' {name} (initial value = {np.array(params_values[j_name])})')

    else:
        nb_disk_structures = len(params_names)
        for i_struct in range(nb_disk_structures):
            print(f'For disk structure #{i_struct+1}:')

            #print(params_values[i_struct])
            for j_name, name in enumerate( params_names[i_struct] ):
                #print(i_struct, j_name)
                print(f' {name} (initial value = {np.array(params_values[i_struct][j_name])})')
    print('')
    return


def print_params_names_and_values_and_bounds(params_names, params_values, params_bounds, params_flat=True, skip_first_line=False):
    '''
    Print for each parameter its name and its value.
    '''
    if not skip_first_line: print(f'\nNames, values and bounds of the disk parameters:')
    #print(params_names)
    #print(params_values)
    #print(params_bounds)

    if params_flat :
        for j_name, name in enumerate( params_names ):
            print(f' {name} (initial value = {np.array(params_values[j_name])}, bounds = {np.array(params_bounds[j_name])})')
        print('')

    else:
        nb_disk_structures = len(params_names)
        for i_struct in range(nb_disk_structures):
            print(f'\n- Disk structure #{i_struct+1}:')
            for j_name, name in enumerate( params_names[i_struct] ):
                print(f' {name} (initial value = {np.array(params_values[i_struct][j_name])}, bounds = {np.array(params_bounds[i_struct][j_name])})')
    print('')
    return



########################################################
############# INITIALIZE DISK PARAMETERS ###############
########################################################

def from_param_list_of_dict_to_param_list_of_list(PARAMS_NAMES_LIST_OF_DICT):
    """ create a initial set of parameters from the initial parameters
        store in the init yaml file
    Args:
        config_file: dic, all the parameters of the exploration algo and PCA read from yaml file

    Returns:
        initial set of parameters
    """
    nb_disk_structures = np.shape(PARAMS_NAMES_LIST_OF_DICT)[0]
   
    params_list_of_list = []
    for i_struct in range( nb_disk_structures ):
        params_names_for_struct_i = PARAMS_NAMES_LIST_OF_DICT[i_struct][f'disk_structure{i_struct+1}']
        params_list_of_list.append(params_names_for_struct_i)
    
    return params_list_of_list


def from_params_names_to_param_bounds(config_file, shape_output='unflat'):
    """ create a initial set of parameters from the initial parameters
        store in the init yaml file
    Args:
        config_file: dic, all the parameters of the exploration algo and PCA read from yaml file

    Returns:
        initial set of parameters
    """
    PARAMS_NAMES = config_file['PARAMS_NAMES']
    nb_disk_structures = len(PARAMS_NAMES)
    
    params_bounds = []
    # Dimension 
    if shape_output == 'unflat':
        for i_struct in range( nb_disk_structures ):  # loop on each disk structure
            params_bounds_for_struct_i = []

            for param in PARAMS_NAMES[i_struct]:  # for a given disk structure, loop on each parameter
                params_bounds_for_struct_i.append(config_file[f'{param}_BOUNDS_STRUCT{i_struct+1}'])
                # Check that minimal and maximal bounds are consistent

                for k_obs in range(len(params_bounds_for_struct_i[-1])):  # for a given disk structure and parameter, note that the parameter can have different values depending on the observation. In principle this should only affect the parameter named SCALING. Thus params_bounds_for_struct_i[-1] is equal to a list of one two-element list, except for the parameter named SCALING, for which params_bounds_for_struct_i[-1] is equal to a list of several two-element lists, several being equal to the number of observations.
                    
                    min, max = params_bounds_for_struct_i[-1][k_obs][0], params_bounds_for_struct_i[-1][k_obs][1]
                    if min > max: raise ValueError(f'The upper boundary for the parameter {param} is smaller than the lower boundary... {max} < {min} !') 
            
            params_bounds.append( params_bounds_for_struct_i) 

    elif shape_output == 'flat':
        for i_struct in range( nb_disk_structures ):  # loop on each disk structure
            
            for param in PARAMS_NAMES[i_struct]:  # for a given disk structure, loop on each parameter
                param_bounds_for_struct_i = config_file[f'{param}_BOUNDS_STRUCT{i_struct+1}']
                # Check that minimal and maximal bounds are consistent

                #print(param_bounds_for_struct_i)

                for k_obs in range(len(param_bounds_for_struct_i)):  # for a given disk structure and parameter, note that the parameter can have different values depending on the observation. In principle this should only affect the parameter named SCALING. Thus params_bounds_for_struct_i[-1] is equal to a list of one two-element list, except for the parameter named SCALING, for which params_bounds_for_struct_i[-1] is equal to a list of several two-element lists, several being equal to the number of observations.
                    params_bounds.append( param_bounds_for_struct_i[k_obs]) 
                    #print(param, params_bounds[-1])
                    min, max = params_bounds[-1][0], params_bounds[-1][1]
                    if min > max: raise ValueError(f'The upper boundary for the parameter {param} is smaller than the lower boundary... {max} < {min} !') 

    return params_bounds

def from_params_names_to_param_init(config_file, shape_output='unflat'):
    """ create a initial set of parameters from the initial parameters
        store in the init yaml file
    Args:
        config_file: dic, all the parameters of the exploration algo and PCA
                            read from yaml file

    Returns:
        initial set of parameters
    """
    PARAMS_NAMES = config_file['PARAMS_NAMES']
    nb_disk_structures = len(PARAMS_NAMES)


    params_init = []
    if shape_output == 'unflat':
        for i_struct in range( nb_disk_structures ):
            params_init_for_struct_i = []
        
            for param in PARAMS_NAMES[i_struct]:
                params_init_for_struct_i.append(config_file[f'{param}_INIT_STRUCT{i_struct+1}'])
            params_init.append( params_init_for_struct_i) 

    else: # flat output
        for i_struct in range( nb_disk_structures ):
            for param in PARAMS_NAMES[i_struct]:
                param_values = config_file[f'{param}_INIT_STRUCT{i_struct+1}']
                for k_obs in range(len(param_values)):
                    params_init.append(config_file[f'{param}_INIT_STRUCT{i_struct+1}'][k_obs])
    return params_init

def from_params_names_unflat_to_params_names_flat_old(config_file):
    """ create a initial set of parameters from the initial parameters
        store in the init yaml file
    Args:
        config_file: dic, all the parameters of the exploration algo and PCA
                            read from yaml file

    Returns:
        initial set of parameters
    """
    PARAMS_NAMES = config_file['PARAMS_NAMES']
    nb_disk_structures = len(PARAMS_NAMES)
    NB_OBS = config_file['NB_OBS']

    params_names = []
    for i_struct in range( nb_disk_structures ):
            for param in PARAMS_NAMES[i_struct]:
                param_values = config_file[f'{param}_INIT_STRUCT{i_struct+1}']
                for k_obs in range(len(param_values)):
                    params_names.append(param)
    return params_names



def from_params_names_unflat_to_params_names_flat(config_file, config_file_param='PARAMS_NAMES'):
    """ create a initial set of parameters from the initial parameters
        store in the init yaml file
    Args:
        config_file: dic, all the parameters of the exploration algo and PCA
                            read from yaml file

    Returns:
        initial set of parameters
    """
    PARAMS_NAMES = config_file['PARAMS_NAMES']
    PARAMS_xx    = config_file[config_file_param]
    nb_disk_structures = len(PARAMS_NAMES)
    NB_OBS       = config_file['NB_OBS']

    params_xx_flat = []
    for i_struct in range( nb_disk_structures ):
            print(i_struct, PARAMS_xx[i_struct])
            for j_param, param in enumerate(PARAMS_NAMES[i_struct]):
                print(param)
                param_values = config_file[f'{param}_INIT_STRUCT{i_struct+1}']
                for k_obs in range(len(param_values)):
                    
                    if config_file_param == 'PARAMS_NAMES':
                        params_xx_flat.append(param)

                    else:
                        print(PARAMS_xx[i_struct][j_param])
                        print(PARAMS_xx[i_struct][j_param][param])
                        params_xx_flat.append(PARAMS_xx[i_struct][j_param][param])
    return params_xx_flat


########################################################
############# INITIALIZE WALKERS #######################
########################################################

def initialize_walkers_backend(config_file, SAVINGDIR):
    """ initialize the MCMC by preparing the initial position of the
        walkers and the backend file

    Args:
        config_file: dic, all the parameters of the MCMC and klip
                            read from yaml file

    Returns:
        if new_backend ==1 then [intial position of the walkers, a clean BACKEND]
        if new_backend ==0 then [None, the loaded BACKEND]
    """

    # if new_backend = 0, reset the backend, if not restart the chains.
    # Be careful if you change the parameters or walkers, 
    # you have to put new_backend = 1
    new_backend   = config_file['NEW_BACKEND']
    nb_walkers    = config_file['NB_WALKERS']
    nb_free_params_tot  = config_file['NB_FREE_PARAMS_TOT'] # = dimension of the MCMC
    fraction_ball = config_file['FRACTION_BALL']
    nb_obs        = config_file['NB_OBS']
    epoch         = config_file['EPOCH']
    display = config_file['DISPLAY_INFO_SIMU_MCMC']
    
    file_prefix = str(np.where(nb_obs == 1, epoch, str(nb_obs) + 'epochs') )

    if new_backend:
        mcmcresultdir = os.path.join(SAVINGDIR, 'results_MCMC') 
        os.makedirs(mcmcresultdir, exist_ok=True)
    else:
        resultdir = config_file['RESULTDIR']
        mcmcresultdir = os.path.join(resultdir, 'results_MCMC')

    params_names = from_params_names_unflat_to_params_names_flat(config_file)
    params_init  = from_params_names_to_param_init(config_file, shape_output='flat')

    if display: print_params_names_and_values(params_names, params_init, params_flat=True)

    # Set up the backend
    # Don't forget to clear it in case the file already exists
    filename_backend = os.path.join(mcmcresultdir, file_prefix + "_backend_file_mcmc.h5")
    backend_init = backends.HDFBackend(filename_backend)

    #############################################################
    # Initialize the walkers. The best technique seems to be
    # to start in a small ball around the a priori preferred position.
    # Don't worry, the walkers quickly branch out and explore the
    # rest of the space.
    if new_backend == 1:
        init_balls = []
        print(f'There are {len(params_init):.0f} parameters in the variable params_init. They should correspond to the parameters to be fitted.')
        for i in range(len(params_init)):
            param = params_names[i]

            if param in ['log_f', 'log_f0', 'log_f1', 'log_f2', 'log_f3']:
                init_balli = np.random.uniform(-10, 10, size=(nb_walkers))
            else:
                init_balli = np.random.uniform(params_init[i] * (1-fraction_ball), params_init[i] * (1+fraction_ball), size=(nb_walkers))
            init_balls.append(init_balli)

        # be careful to the shape of the array, previously done via the function np.dstack
        # p0 = np.dstack((init_ball0, init_ball1, init_ball2, init_ball3, init_ball4, init_ball5))
        # now
        p0 = np.array([np.array(init_balls).transpose()])
        
        backend_init.reset(nb_walkers, nb_free_params_tot)
        return p0[0], backend_init

    return None, backend_init

########################################################
################## LOG PRIORS ##########################
########################################################

def logp(params, dico=None, params_flat=True):
    params_bounds = dico.get('params_bounds', 'PROBLEM')

    #if len(params_bounds)[0] != len(params): raise ValueError(f'The number of parameters listed in the list "bounds" {len(params_bounds)} should be the same than the number of parameters in "params" ({len(params)}). \n bounds = {params_bounds} \n\n params = {params}')
    nb_disk_structures = len(params_bounds)
    
    #print('params_bounds', params_bounds)
    #print('params', params)

    # Check if a parameter is beyond
    if params_flat : # the list params is flat and the list params_bounds is almost flat (dimension of list params * 2)
        n = len(params)
        params_names  = dico.get('params_names_flat', 'PROBLEM')
        for i in range(n):
            if params_bounds[i][0] != None :
                if params[i] < params_bounds[i][0] : 
                    print(f' The tested parameter {params_names[i]} ({params[i]}) is out of bounds. It should be bigger than {params_bounds[i][0]}.')
                    return -np.inf
            if params_bounds[i][1] != None :
                if params[i] > params_bounds[i][1] :
                    print(f' The tested parameter {params_names[i]} ({params[i]} is out of bounds. It should be smaller than {params_bounds[i][1]}.')
                    return -np.inf
    else :
        params_names  = dico.get('params_names_unflat', 'PROBLEM')
        for i_struct in range( nb_disk_structures ): # loop on each disk structure
            #print('params_bounds[i_struct]', params_bounds[i_struct])

            #print('params[i_struct]', params[i_struct])

            #print('')
            
            for j_param in range(len(params[i_struct])): # for a given disk structure, loop on each parameter
                #print(i_struct, j_param)
                bounds_struct_i_param_j = params_bounds[i_struct][j_param]  # for a given disk structure and parameter, parameters can have different values depending on the observation. In principle this should only affect the parameter named SCALING. Thus bounds_istruct_jparam is equal to a list of one two-element list, except for the parameter named SCALING, for which bounds_istruct_jparam is equal to a list of several two-element lists, several being equal to the number of observations.
                #print('bounds_struct_i_param_j', bounds_struct_i_param_j, params[i_struct][j_param])
                
                ##print('bounds_istruct_jparam', bounds_struct_i_param_j)
                for k_obs in range(len(bounds_struct_i_param_j)): 
                    #print('\n',k_obs,'/',len(bounds_struct_i_param_j))
                    bounds = bounds_struct_i_param_j[k_obs]
                    #print('bounds', bounds)
                    #print('params[i_struct][j_param][k_obs]', params[i_struct][j_param][k_obs])
                    if bounds[0] != None :
                        #print('bounds', bounds)
                        #print(i_struct, j_param, k_obs)
                        #print(params)
                        #time.sleep(1)
                        #print('params[i_struct][j_param]', params[i_struct][j_param])
                        #print('params[i_struct][j_param][k_obs]',params[i_struct][j_param][k_obs])
                        
                        if params[i_struct][j_param][k_obs] < bounds[0] : return -np.inf

                    if bounds[1] != None :
                        if params[i_struct][j_param][k_obs] > bounds[1] : return -np.inf

    return 0


########################################################
################ LOG LIKELIHOOD ########################
########################################################

def logl(params, dico=None, params_flat=True):
    """ measure the log of the likelihood of the parameter set.
        create disk
        convolve by the PSF (psf is global)
        do the forward modeling (diskFM obj is global)
        nan out when it is out of the zone (zone mask is global)
        subctract from data and divide by noise (data and noise are global)

    Args:
        params: list of parameters of the MCMC

    Returns:
        Chisquare

    Note: works for a given number of parameters (radius, PA, inclination, g, scaling, (log_f) )
    """
    ll = -0.5 * chisquare_params(params, dico=dico, params_flat=params_flat)
    return ll

########################################################
################ SUM OF THE LOGS  ######################
########################################################

def reshape_list_of_params_from_1D_into_3D(params_to_be_reshaped, dico):
    nb_disk_structures = dico.get("nb_disk_structures")
    params_example = dico.get("params_example_unflat")

    #print('\n\n\n params_example')
    #print(params_example)

    #print('\n\n\n')

    #raise ValueError('end')
    params_reshaped = copy.deepcopy(params_example)
    
    count=0
    for i in range(len(params_example)):
        for j in range(len(params_example[i])):
            for k in range(len(params_example[i][j])):
                params_reshaped[i][j][k] = params_to_be_reshaped[count]
                count +=1

    #print('\n\n\n params_reshaped')
    #print(params_reshaped)

    #print('\n\n\n')

    #raise ValueError('end')


    return params_reshaped


def lnpb_mcmc(params, **kwargs):
    """ sum the logs of the priors (return of the logp function)
        and of the likelihood (return of the logl function)

    Args:
        params: list of parameters of the MCMC. Must be a 1D list

    Returns:
        log of priors + log of likelihood

    Remark: the list of params must be reshaped in a list of list. First axis represents the number of disk structures, the second axis the parameters. For some parameters, their values can be a list (e.g. for the parameter SCALING).
     """
    #print('\nparams')
    #print(params)
    kwargs['params_1D'] = params
    #params_reshaped   = reshape_1D_list_of_params_into_2D_list_of_params(params, kwargs)
    #print('\nparams')
    #print(params_reshaped)
    #print('')
    # Log of the priors
    #lp = logp(params_reshaped, dico=kwargs, flat=False)
    lp = logp(params, dico=kwargs, params_flat=True)
    
    if not np.isfinite(lp): 
        return -np.inf

    # Log of the likelihood
    #ll = logl(params_reshaped, dico=kwargs)
    ll = logl(params, dico=kwargs, params_flat=True)
    return lp + ll

#######################################################
#######################################################

def lnpb(params, dico=None, params_flat=True):
    """ sum the logs of the priors (return of the logp function)
        and of the likelihood (return of the logl function)

    Args:
        params: list of parameters. Must be a 2D list

    Returns:
        log of priors + log of likelihood

    """
    # Log of the priors
    lp = logp(params, dico=dico, params_flat=params_flat)
    if not np.isfinite(lp): return -np.inf

    # Log of the likelihood
    ll = logl(params, dico=dico, params_flat=params_flat)
    return lp + ll


########################################################
######## AMOEBA ## FUNCTION TO MINIMIZE  ###############
########################################################

def chisquare_params_NelderMead(params, kwargs):
    return chisquare_params(params, dico=kwargs, params_flat='flat')

#######################################################
#### Generate disk model: a, PA, inc, g, scaling ######
#######################################################


def update_params_init_values_for_given_disk_model(dico, disk_struc=1):
    # for this given disk structure, initialize the disk model parameters with initial values (fixed parameters will remain the same, free parameters will later be updated)
    #dico = update_params_init_values_for_given_disk_model(dico, j_struct+1)
                
    dico['rad_init'] = dico[f'rad_init_struc{disk_struc}']
    dico['pa_init']  = dico[f'pa_init_struc{disk_struc}']
    dico['inc_init'] = dico[f'inc_init_struc{disk_struc}']
    dico['g1_init']  = dico[f'g1_init_struc{disk_struc}']
    dico['g2_init']  = dico[f'g2_init_struc{disk_struc}']
    dico['argperi_init'] = dico[f'argperi_init_struc{disk_struc}']
    dico['ecc_init']   = dico[f'ecc_init_struc{disk_struc}']
    dico['ksi0_init']  = dico[f'ksi0_init_struc{disk_struc}']
    dico['gamma_init'] = dico[f'gamma_init_struc{disk_struc}']
    dico['beta_init']  = dico[f'beta_init_struc{disk_struc}']
    dico['alpha_init'] = dico[f'alpha_init_struc{disk_struc}']
    dico['ain_init']   = dico[f'ain_init_struc{disk_struc}']
    dico['aout_init']  = dico[f'aout_init_struc{disk_struc}']
    return dico

def generate_disk_model(params_values, dico = None):
    """ call the disk model from a set of parameters. 1g SPF
        use global variables DIMENSION, PIXSCALE_INS and DISTANCE_STAR

    Args:
        params: list of parameters of the MCMC
        here 5 params: a, PA, inc, g, scaling

    Returns:
        a 2d model
    """
    # Access keyword arguments from kwadrgs
    params_names  = dico.get('params_names_1model','PROBLEM')
    #print('l405', params_names)
    dimension     = dico.get('dimension', 'PROBLEM')
    plate_scale  = dico.get('plate_scale', 'PROBLEM')
    distance_star = dico.get('distance_star', 'PROBLEM')
    disk_model_polar = dico.get('disk_model_polar', 'PROBLEM')
    convention_unit  = dico.get('convention_unit', 'PROBLEM')
    disk_struc = dico.get('disk_struc', 'PROBLEM') # 1 = if disk structure #1, 2 = if disk structure #2, etc
    idx_obs    = dico.get('idx_obs', 'PROBLEM') # 1 = if obs #1, 2 = obs #2, etc: useful for the value of the parameter SCALING
    display    = dico.get('display', 0)

    if type(params_names) == type(''): raise ValueError('There is a problem with the value of names.')
    
    if len(params_names) != len(params_values): 
        raise ValueError(f'The number of parameters listed in the list "NAMES" should be the same than the number of parameters in "params". \nNAMES = {params_names} \nparams = {params_values}')
    
    # Check if some extra keyword arguments were effectively given
    if disk_struc == 'PROBLEM': raise ValueError('There is a problem with the value of disk_struc.')
    if type(dimension) == type(''): raise ValueError('There is a problem with the value of dimension.')
    if type(plate_scale) == type(''): raise ValueError('There is a problem with the value of plate_scale.')
    if type(distance_star) == type(''): raise ValueError('There is a problem with the value of distance_star.')
    if type(disk_model_polar) == type(''): raise ValueError('There is a problem with the value of disk_model_polar.')
    if convention_unit == 'PROBLEM': raise ValueError('There is a problem with the value of convention_unit.')

    if display: 
        print_params_names_and_values(params_names, params_values, params_flat=True)

    # Assigned the values of the fixed parameters
    if 'RAD' not in params_names: r1  = dico.get(f'rad_init_struct{disk_struc}', ['PROBLEM'])[0]
    if 'PA' not in params_names:  pa  = dico.get(f'pa_init_struct{disk_struc}',  ['PROBLEM'])[0]
    if 'INC' not in params_names: inc = dico.get(f'inc_init_struct{disk_struc}', ['PROBLEM'])[0]
    if 'G1' not in params_names:  g1  = dico.get(f'g1_init_struct{disk_struc}',  ['PROBLEM'])[0]
    if 'G2' not in params_names:  g2  = dico.get(f'g2_init_struct{disk_struc}',  ['PROBLEM'])[0]
    if 'ARGPERI' not in params_names: argperi = dico.get(f'argperi_init_struct{disk_struc}', ['PROBLEM'])[0]
    if 'ECC' not in params_names:  ecc    = dico.get(f'ecc_init_struct{disk_struc}', ['PROBLEM'])[0]
    if 'KSI0' not in params_names: ksi0   = dico.get(f'ksi0_init_struct{disk_struc}',['PROBLEM'])[0]
    if 'GAMMA' not in params_names: gamma = dico.get(f'gamma_init_struct{disk_struc}',['PROBLEM'])[0]
    if 'BETA' not in params_names:  beta  = dico.get(f'beta_init_struct{disk_struc}', ['PROBLEM'])[0]
    if 'ALPHA' not in params_names: alpha = dico.get(f'alpha_init_struct{disk_struc}',['PROBLEM'])[0]
    if 'AIN' not in params_names:   ain   = dico.get(f'ain_init_struct{disk_struc}', ['PROBLEM'])[0]
    if 'AOUT' not in params_names:  aout  = dico.get(f'aout_init_struct{disk_struc}', ['PROBLEM'])[0]
    if 'SCALING' not in params_names:  scaling  = dico.get(f'scaling_init_struct{disk_struc}', ['PROBLEM'])[0]

    # Assigned the values of the free parameters
    for i, name in enumerate(params_names):
        if name == 'SCALING': scaling = params_values[i][idx_obs] ; #print('scaling', scaling)
        if name == 'RAD':   r1   = params_values[i][0]
        if name == 'PA':    pa   = params_values[i][0]
        if name == 'INC':   inc  = params_values[i][0]
        if name == 'G1':    g1   = params_values[i][0]
        if name == 'G2':    g2   = params_values[i][0]
        if name == 'AIN':   ain  = params_values[i][0]
        if name == 'AOUT':  aout = params_values[i][0]
        if name == 'ARGPERI': argperi = params_values[i][0]
        if name == 'ECC':   ecc   = params_values[i][0]
        if name == 'KSI0':  ksi0  = params_values[i][0]
        if name == 'GAMMA': gamma = params_values[i][0]
        if name == 'BETA':  beta  = params_values[i][0]
        if name == 'ALPHA': alpha = params_values[i][0]

        
    if 'PROBLEM' in [r1, pa, inc, g1, argperi, ecc, ksi0, gamma, beta, ain, aout, scaling] :
        raise ValueError(f'One of the disk parameter was forgotten in the parameters configuration file. \n radius = {r1} au \n PA = {pa} deg \n inc = {inc} \n g1 = {g1} \n argperi = {argperi} \n ecc = {ecc} \n ksi0 = {ksi0} \n gamma = {gamma} \n beta = {beta} \n alpha = {alpha} \n ain = {ain} \n aout = {aout}')

    if convention_unit == 'MCMC':
        scaling = 10**scaling #mt.exp(params[0])
        inc = np.arccos(inc) * 180/np.pi

    # Generate the model
    model = vip.fm.scattered_light_disk.ScatteredLightDisk(nx=dimension,
                               ny=dimension,
                               distance=distance_star,
                               itilt=inc,
                               omega=argperi,
                               pxInArcsec=plate_scale,
                               pa= pa,
                               density_dico={
                                   'name': '2PowerLaws',
                                   'ain': ain,
                                   'aout': aout,
                                   'a': r1,
                                   'e': ecc,
                                   'ksi0': ksi0,
                                   'gamma': gamma,
                                   'beta': beta
                               },
                               spf_dico={
                                   'name': 'HG',
                                   'g': g1,
                                   'polar': disk_model_polar
                               })
    
    return model.compute_scattered_light() * scaling


########################################################
############# COMPUTE ITS CHISQUARE ####################
########################################################

def chisquare_params(params, dico = None, params_flat=True):
    """ measure the Chisquare of the parameter set.
        create disk
        convolve by the PSF (psf is global)
        do the forward modeling (diskFM obj is global)
        nan out when it is out of the zone (zone mask is global)
        subctract from data and divide by noise (data and noise are global)

    Args:
        params: list of parameters of the MCMC

    Returns:
        Chisquare

    Note: works for 5 or 6 parameters, for 1, 2, 3? and 4? epochs.
    """
    # Access extra keyword arguments from kwargs
    nb_obs = dico.get('nb_obs', 'PROBLEM')
    TYPE_OBS_ALL = dico.get('type_obs_all', 'PROBLEM')
    PARAMS_NAMES = dico.get('params_names_flat', 'PROBLEM')

    do_deep_flattening = dico.get('do_deep_flattening', 1)


    if not params_flat : # the list of parameters is not flat
        #print(f'\nThe input parameters "params" list is in 3D. Check:\n{params}.\n')
        params3D = params
        params1D = list(deepflatten(list(params3D)))
        #print(f'Here the reshaped list of input parameters "params" list in 1D: \n{params1D}.\n')

    else: # the list of parameters is flat
        #print(f'\nThe input parameters "params" list is in 1D. Check:\n{params}.\n')
        params1D = params
        params3D = reshape_list_of_params_from_1D_into_3D(params1D, dico)
        #print(f'Here the reshaped list of input parameters "params" list in 3D: \n{params3D}.\n')

    dico['params_1D'] = params1D

    # Deep flattens a list
    #if do_deep_flattening and 0: 
        #print('Before deep flattening:\n', params)
        #params1D = list(deepflatten(list(params)))
        #dico['params_1D'] = params1D
        #print('After deep flattening:\n', params1D)
    

    # Check if some extra keyword arguments were effectively given
    if nb_obs == 'PROBLEM': raise ValueError('There is a problem with the value of nb_obs.')
    if nb_obs > 1 and type(TYPE_OBS_ALL) == type('PROBLEM'): raise ValueError('There is a problem with the value of TYPE_OBS_ALL.')

    #print('\n\n', params, '\n\n')

    if 'log_f' in PARAMS_NAMES or 'logf' in PARAMS_NAMES:
        Chisquare = chisquare_logf(params3D, dico = dico)
    else:
        Chisquare = chisquare(params3D, dico = dico)

    return Chisquare




def chisquare(params_3D, dico = None):
    """ measure the Chisquare of the parameter set.
        create disk
        convolve by the PSF (psf is global)
        do the forward modeling (diskFM obj is global)
        nan out when it is out of the zone (zone mask is global)
        subctract from data and divide by noise (data and noise are global)

    Args:
        params: list of parameters of the MCMC

    Returns:
        Chisquare
    """
    # Access extra keyword arguments from dictionary
    display        = dico.get('display', 0)
    #dico['display'] = 0
    nb_obs         = dico.get('nb_obs', 1)
    type_obs_all   = dico.get('type_obs_all', 'PROBLEM')
    disk_model_polar_all = dico.get('disk_model_polar_all', 'PROBLEM')
    do_robust_convolution_all = dico.get('do_robust_convolution_all', 1)
    im_pa_all        = dico.get('im_pa_all', 'PROBLEM')
    psf_all          = dico.get('psf_all', 'PROBLEM')
    mask2minimize_all= dico.get('mask2minimize_all', 'PROBLEM')
    noise_map_all    = dico.get('noise_map_all', 'PROBLEM')
    science_data_all = dico.get('science_data_all', 'PROBLEM')
    dimension_all    = dico.get('dimension_all', 'PROBLEM')
    nb_resel_all     = dico.get('nb_resel_all', 'PROBLEM')
    nb_free_params_tot        = dico.get('nb_free_params_tot', 'PROBLEM')
    nb_free_params_per_obs_all= dico.get('nb_free_params_per_obs_all', 'PROBLEM')
    convention_unit           = dico.get('convention_unit', 'PROBLEM')
    save_some_results = dico.get('save_some_results', False)
    save_full_results = dico.get('save_full_results', False)
    simu_resultdir    = dico.get('simu_resultdir','None')
    pa_array_all     = dico.get('pa_array_all', 'PROBLEM')
    iwa_all          = dico.get('iwa_all', 'MASK_RAD')
    nmodes_all       = dico.get('nmodes_all', 'PROBLEM')
    plate_scale_all = dico.get('plate_scale_all', 'PROBLEM')
    params_names     = dico.get('params_names_unflat', 'PROBLEM')
    nb_disk_structures = dico.get('nb_disk_structures', 'PROBLEM')  
    params_1D          = dico.get('params_1D','PROBLEM')  

    # Check if some extra keyword arguments were effectively given
    if nb_obs>1 and type(type_obs_all) == type('PROBLEM'): raise ValueError('There is a problem with the value of type_obs_all.')
    if type(im_pa_all) == type(''): raise ValueError('There is a problem with the value of im_pa_all.')
    if type(psf_all) == type(''): raise ValueError('There is a problem with the value of psf_all.')
    if type(mask2minimize_all) == type(''): raise ValueError('There is a problem with the value of mask2minimize.')
    if type(noise_map_all) == type(''): raise ValueError('There is a problem with the value of noise_all.')
    if type(pa_array_all) == type(''): raise ValueError('There is a problem with the value of pa_array_all.')
    if type(science_data_all) == type(''): raise ValueError('There is a problem with the value of science_data_all.')
    if type(nb_resel_all) == type(''): raise ValueError('There is a problem with the value of nresel.')
    if type(nb_free_params_tot) == type(''): raise ValueError('There is a problem with the value of nb_free_params_tot.')
    if type(nb_free_params_per_obs_all) == type(''): raise ValueError(f'There is a problem with the value of nb_free_params_per_obs_all, which is {nb_free_params_per_obs_all}')
    if type(iwa_all) == type(''): raise ValueError('There is a problem with the value of mask_rad.')
    if type(nmodes_all) == type(''): raise ValueError('There is a problem with the value of nmodes.')
    if convention_unit == 'PROBLEM': raise ValueError('There is a problem with the value of convention_unit.')
    if type(nb_obs) == type(''): raise ValueError('There is a problem with the value of nb_obs.')
    #if type(params_1D) == type(''): raise ValueError('There is a problem with the value of params_1D.')
    
    if display: print('------------------------------------------------------------------------------------')
    for i_obs in range(nb_obs): # loop on each observation
        if display: print(f'Consider the observation #{i_obs+1}')
        dico['idx_obs']   = int(i_obs)

        type_obs      = type_obs_all[i_obs]
        science_data  = science_data_all[i_obs]
        noise_map     = noise_map_all[i_obs]
        pa_array      = pa_array_all[i_obs]
        psf           = psf_all[i_obs]
        nmodes        = nmodes_all[i_obs]
        iwa           = iwa_all[i_obs]
        mask2minimize = mask2minimize_all[i_obs]
        nb_resel      = nb_resel_all[i_obs]
        nb_free_params_per_obs = nb_free_params_per_obs_all[i_obs]
        do_robust_convolution = do_robust_convolution_all[i_obs]
        im_pa = im_pa_all[i_obs] # relevant only for polarized intensity data and if do_robust_convolution is set to 1

        dico['plate_scale']  = plate_scale_all[i_obs]
        dico['dimension']    = dimension_all[i_obs]
        dico['nb_resel']     = nb_resel_all[i_obs]
        dico['disk_model_polar'] = disk_model_polar_all[i_obs]


        # Case 1: the data are total intensity data
        if type_obs == 'total_intensity':    
            cube_diff = np.copy(science_data)  

            models = []

            for j_struct in range(nb_disk_structures): # loop on each disk structure
                if display: print(f'Consider the disk structure #{j_struct+1}')

                dico['disk_struc'] = int(j_struct+1)

                params_values = params_3D[j_struct]
                dico['params_names_1model'] = params_names[j_struct]

                #print('l653', params_values)
                #print('l655', params_names[j_struct])

                # Generate the disk model
                #params = np.array(params)
                #np.array([params[0],params[1],params[2],params[3],params[4]])
                models.append(generate_disk_model(params_values, dico = dico))

                models = np.array(models)

            full_model = np.nansum(models, axis=0)    
            #print(f'\n\n CHECK WHEN SEVERAL DISK STRUCTURES THAT THE SHAPE OF full_model IS A SHAPE OF AN IMAGE { np.shape(full_model)} \n\n')
            # Rotate the disk model for different angles and convolve it by the PSF
            full_modelconvolved = vip.fm.cube_inject_fakedisk(full_model, -np.array(pa_array), psf=psf)

            # Compute the residuals and the chisquare
            # Remove the disk from the observation
            cube_diff -= full_modelconvolved

            # Reduce the observation
            try:
                res_full_map = vip.psfsub.pca_fullfr.pca(cube_diff, pa_array, ncomp=nmodes, mask_center_px=iwa, imlib='opencv', full_output=False)
            except: 
                os.makedirs('PROBLEM', exist_ok=True)
                suffix_nb_obs_nb_struct = f"_obs{i_obs+1:.0f}_struc{j_struct+1:.0f}".replace('.','p')
                fits.writeto('PROBLEM'+f'/disk_model_{suffix_nb_obs_nb_struct}_PROBLEM.fits',full_model, overwrite=True)
                fits.writeto('PROBLEM'+f'/disk_model_convolved_{suffix_nb_obs_nb_struct}_PROBLEM.fits',full_modelconvolved, overwrite=True)
                fits.writeto('PROBLEM'+f'/disk_CUBE_DIFF_{suffix_nb_obs_nb_struct}_PROBLEM.fits',cube_diff, overwrite=True)

                raise ValueError(f'The PCA reduction did not converge for the observation {i_obs+1:.0f} when after subtracting the model of the disk structure #{j_struct:.0f}. The disk parameters used are the following\n{params_3D}')

            res_full_map_snr = res_full_map / noise_map
            Chisquare = np.nansum(res_full_map_snr * res_full_map_snr * mask2minimize)

        # Case 2: the data are polarized intensity data
        elif type_obs in ['polarized_intensity', 'polarised_intensity', 'polarized intensity', 'polarised intensity', 'polar']:
            models = []
            for j_struct in range(nb_disk_structures): # loop on each disk structure
                if display: print(f'Consider disk structure #{j_struct+1}')
                dico['disk_struc'] = int(j_struct+1)
                params_values = params_3D[j_struct]
                dico['params_names_1model'] = params_names[j_struct]
                
                # Generate the disk model         
                models.append(generate_disk_model(params_values, dico = dico))
                full_model = np.nansum(models, axis=0)    

                #print(f'\n\n CHECK WHEN SEVERAL DISK STRUCTURES THAT THE SHAPE OF full_model IS A SHAPE OF AN IMAGE { np.shape(full_model)} \n\n')

            if do_robust_convolution:
                # In particular important for close-in or asymmetric disks. See Heikamp & Keller 2019
                Q_neg = full_model*np.cos(2*im_pa)
                U_neg = full_model*np.sin(2*im_pa)
                Q_neg_convolved = convolve_fft(Q_neg, psf)#, mode='same')
                U_neg_convolved = convolve_fft(U_neg, psf)#, mode='same')
                full_modelconvolved = (Q_neg_convolved*np.cos(2*im_pa)+U_neg_convolved*np.sin(2*im_pa)) # corresponds to Qphi 
        
            else: full_modelconvolved = convolve_fft(full_model, psf, boundary='wrap')

            res_full_map = (science_data - full_modelconvolved)
            res_full_map_snr = (science_data - full_modelconvolved)  / noise_map
            Chisquare = np.nansum(res_full_map_snr * res_full_map_snr * mask2minimize)
            

        # Save the results
        if save_some_results or save_full_results:
            # if yes, either save only some results or all of them
            # some: include the tested model, two residuals maps (the nominal one and the one normalized by the noise) and the parameters
            suffix_chisquare = "test" # f"_{Chisquare:.0f}".replace('.','p')
            suffix_chisquare =  f"_{Chisquare:.0f}".replace('.','p')
            suffix_nb_obs = f"_obs{i_obs+1:.0f}".replace('.','p')

            if type_obs == 'total_intensity': full_modelconvolved = convolve_fft(full_model, psf, boundary='wrap') # just save the model convolved at one parallactic angle position...   

            # Save some results
            if type_obs == 'total_intensity': 
                full_modelconvolved = convolve_fft(full_model, psf, boundary='wrap') # just save the model convolved at one parallactic angle position...
            fits.writeto(simu_resultdir+f'/disk_model_convolved{suffix_chisquare}{suffix_nb_obs}.fits',full_modelconvolved, overwrite=True)  
            fits.writeto(simu_resultdir+f'/residuals{suffix_chisquare}{suffix_nb_obs}.fits', res_full_map, overwrite=True)   
            fits.writeto(simu_resultdir+f'/residuals_snr{suffix_chisquare}{suffix_nb_obs}.fits', res_full_map, overwrite=True)
            fits.writeto(simu_resultdir+f'/params{suffix_chisquare}.fits', np.array(params_1D), overwrite=True)  
            #fits.writeto(os.path.join(simu_resultdir,f'params.fits'), np.array(params_1D), overwrite=True)  
            

            if save_full_results: # save additional files
                fits.writeto(simu_resultdir+f'/disk_model{suffix_chisquare}{suffix_nb_obs}.fits',full_model, overwrite=True)  

                if nb_disk_structures!=1: # for each disk structure, save its tested model
                    for j_struct in range(nb_disk_structures): 
                        suffix_nb_obs_nb_struct = f"_obs{i_obs+1:.0f}_struc{j_struct+1:.0f}"
                        fits.writeto(simu_resultdir+f'/disk_model{suffix_chisquare}{suffix_nb_obs_nb_struct}.fits', models[j_struct], overwrite=True)

                        if type_obs == 'total_intensity': full_modelconvolved = convolve_fft(models[j_struct], psf, boundary='wrap') # just save the model convolved at one parallactic angle position...
                        fits.writeto(simu_resultdir+f'disk_model_convolved{suffix_chisquare}{suffix_nb_obs_nb_struct}.fits',full_modelconvolved, overwrite=True)  
                    
                # regarding polarized intensity, save files about the robust convolution
                if type_obs in ['polarized_intensity', 'polarised_intensity', 'polar'] and do_robust_convolution:
                    fits.writeto(simu_resultdir+f'/disk_model_Q_convolved{suffix_chisquare}{suffix_nb_obs}.fits',-Q_neg_convolved, overwrite=True)      
                    fits.writeto(simu_resultdir+f'/disk_model_U_convolved{suffix_chisquare}{suffix_nb_obs}.fits',-U_neg_convolved, overwrite=True)  

                if type_obs == 'total_intensity': fits.writeto(simu_resultdir+f'/cube_obs-model_before_processing{suffix_chisquare}{suffix_nb_obs}.fits', cube_diff, overwrite=True)   
        
        Chisquare_red = Chisquare/(nb_resel-nb_free_params_per_obs-1)    

        if display: 
            print(f'-> Summary: Considering the observation #{i_obs+1} using {nb_disk_structures} disk structure(s), the simulation gives')
            #print_params_names_and_values_for_unflatten_list(params_names, [params_values], nb_obs, nb_disk_structures)
            print(f'  chisquare = {Chisquare:.4e} i.e. {Chisquare:.0f}, reduced chisquare = {Chisquare_red:.2f}')

    if display: print('------------------------------------------------------------------------------------')

    return Chisquare


def chisquare_logf(params, dico = None):
    """ measure the Chisquare of the parameter set.
        create disk
        convolve by the PSF (psf is global)
        do the forward modeling (diskFM obj is global)
        nan out when it is out of the zone (zone mask is global)
        subctract from data and divide by noise (data and noise are global)

    Args:
        params: list of parameters of the MCMC

    Returns:
        Chisquare
    """
    startTime =  datetime.now() 
    
    # Access extra keyword arguments from dictionary
    display = dico.get('display', 0)
    nb_obs = dico.get('nb_obs','PROBLEM')
    type_obs_all = dico.get('type_obs_all', 'PROBLEM')
    do_robust_convolution = dico.get('do_robust_convolution', 1)
    im_pa = dico.get('im_pa', 'PROBLEM')
    psf_all = dico.get('psf_all', 'PROBLEM')
    mask2minimize = dico.get('mask2minimize', 'PROBLEM')
    noise_all = dico.get('noise_all', 'PROBLEM')
    pa_array_all = dico.get('pa_array_all', 'PROBLEM')
    science_data_all = dico.get('science_data_all', 'PROBLEM')
    #red_data  = dico.get('red_data', 'PROBLEM')
    nresel = dico.get('nresel', 'PROBLEM')
    nparams = dico.get('nparams', 5)
    nmodes = dico.get('nmodes', 'PROBLEM')
    mask_rad = dico.get('mask_rad', 'PROBLEM')
    convention_unit = dico.get('convention_unit', 'PROBLEM')
    plate_scale_all = dico.get('plate_scale_all', 'PROBLEM')
    #dico['plate_scale'] = plate_scale_all
    save_detail_results = dico.get('save_detail_results', False)
    save_intermediate_results = dico.get('save_intermediate_results', False)
    detail_resultdir = dico.get('detail_resultdir','None')
    intermediate_resultdir = dico.get('intermediate_resultdir','None')
    dico['obs_id'] = ''
    dico['names'] = dico.get('names', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if nb_obs>1 and type(type_obs_all) == type('PROBLEM'): raise ValueError('There is a problem with the value of type_obs_all.')
    if type(im_pa) == type(''): raise ValueError('There is a problem with the value of im_pa.')
    if type(psf_all) == type(''): raise ValueError('There is a problem with the value of psf_all.')
    if type(mask2minimize) == type(''): raise ValueError('There is a problem with the value of mask2minimize.')
    if type(noise_all) == type(''): raise ValueError('There is a problem with the value of noise_all.')
    if type(pa_array_all) == type(''): raise ValueError('There is a problem with the value of pa_array_all.')
    if type(science_data_all) == type(''): raise ValueError('There is a problem with the value of science_data_all.')
    if type(nresel) == type(''): raise ValueError('There is a problem with the value of nresel.')
    if type(nparams) == type(''): raise ValueError('There is a problem with the value of nparams.')
    if type(mask_rad) == type(''): raise ValueError('There is a problem with the value of mask_rad.')
    if type(nmodes) == type(''): raise ValueError('There is a problem with the value of nmodes.')
    if convention_unit == 'PROBLEM': raise ValueError('There is a problem with the value of convention_unit.')
    if type(nb_obs) == type(''): raise ValueError('There is a problem with the value of nb_obs.')
    if type(names) == type(''): raise ValueError('There is a problem with the value of names.')
    #if save_detail_results == True and type_obs == 'total_intensity' and type(red_data) == 'PROBLEM': raise ValueError('There is a problem with the value of red_data.')

    #if display: print('In function chisquare_6params_1obs_polar() ')
    
    if type_obs_all == 'total_intensity':        
        # Generate disk model
        #params = 
        #np.array([params[0],params[1],params[2],params[3],params[4],params[5]])
        log_f = params[-1]
        
        model = generate_disk_model(params, dico = dico)

        # Rotate the disk model for different angles and convolve it by the PSF
        modelconvolved = vip.fm.cube_inject_fakedisk(model, -pa_array_all, psf=psf_all)

        # Compute the residuals and the chisquare
        # Remove the disk from the observation, i.e., data - model (3D)
        CUBE_DIFF = (science_data_all - modelconvolved)

        # Reduce the observation
        try:
            im_pca = vip.psfsub.pca_fullfr.pca(CUBE_DIFF, pa_array_all, ncomp=nmodes, mask_center_px=mask_rad, imlib='opencv', full_output=False)
        except: 
            raise ValueError(f'The PCA reduction did not converge. The disk parameters used are the following: {params}')
        
        sigma2 = (noise_all**2 + np.exp(log_f*2) * modelconvolved**2) 

        Chisquare = np.nansum( ( im_pca * mask2minimize ) **2  / sigma2 + np.log(sigma2) * mask2minimize ) # on fait attention de bien compter uniquement les régions dans le masque
        Chisquare_red = Chisquare/(nresel-nparams-1)

        if save_detail_results:
            modelconvolved0 = convolve_fft(model, psf_all, boundary='wrap')
            
            fits.writeto(os.path.join(detail_resultdir,'disk_model.fits'),model, overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'disk_model_convolved.fits'),modelconvolved0, overwrite=True)      
            #fits.writeto(os.path.join(detail_resultdir,'disk_model_convolved_cube.fits'), modelconvolved, overwrite=True)
            #fits.writeto(os.path.join(detail_resultdir,'residuals_cube.fits'), CUBE_DIFF, overwrite=True)
            #fits.writeto(os.path.join(detail_resultdir,'residuals.fits'), DIFF0, overwrite=True)    

            fits.writeto(os.path.join(detail_resultdir,'residuals_fm.fits'), im_pca, overwrite=True)      
            fits.writeto(os.path.join(detail_resultdir,'residuals_fm_snr.fits'), im_pca**2/sigma2, overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'residuals_fm_snr_plus_extra_term.fits'), im_pca**2/sigma2 + np.log(sigma2), overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'params.fits'), params, overwrite=True)

        elif save_intermediate_results:
            dt =  datetime.now()  - startTime
            suffix = "_{:.2f}min_{:.0f}_{:.2f}".format(dt.seconds/60, Chisquare, Chisquare_red)
            modelconvolved0 = convolve_fft(model, psf_all, boundary='wrap')

            fits.writeto(os.path.join(detail_resultdir,'residuals_fm.fits'), im_pca, overwrite=True)      
            fits.writeto(os.path.join(intermediate_resultdir,'params{}.fits'.format(suffix)), params, overwrite=True)
            fits.writeto(os.path.join(intermediate_resultdir,'disk_model_convolved{}.fits'.format(suffix)), modelconvolved0, overwrite=True)

    elif type_obs_all == 'polar':
        # Generate disk model        
        #params = np.array([params[0],params[1],params[2],params[3],params[4],params[5]])
        log_f = params[-1]
        model = generate_disk_model(params, dico = dico)

        if do_robust_convolution:
            # In particular important for close-in or asymmetric disks. See Heikamp & Keller 2019
            Q_neg = model*np.cos(2*im_pa)
            U_neg = model*np.sin(2*im_pa)
            Q_neg_convolved = convolve_fft(Q_neg, psf_all)#, mode='same')
            U_neg_convolved = convolve_fft(U_neg, psf_all)#, mode='same')
            modelconvolved = (Q_neg_convolved*np.cos(2*im_pa)+U_neg_convolved*np.sin(2*im_pa)) # corresponds to Qphi 
    
        else: modelconvolved = convolve_fft(model, psf_all, boundary='wrap')

        sigma2 = noise_all**2 + np.exp(log_f*2) * modelconvolved**2 # take more realistic noise into account
        Chisquare = np.nansum( ( (science_data_all - modelconvolved) * mask2minimize ) **2  / sigma2 + np.log(sigma2) * mask2minimize ) # on fait attention de bien compter uniquement les régions 
        Chisquare_red = Chisquare/(nresel-nparams-1)

        if save_detail_results:               
            fits.writeto(os.path.join(detail_resultdir,'disk_model.fits'), model, overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'disk_model_convolved.fits'),modelconvolved, overwrite=True)      
            fits.writeto(os.path.join(detail_resultdir,'residuals.fits'), (science_data_all - modelconvolved)**2, overwrite=True)    
  
            fits.writeto(os.path.join(detail_resultdir,'residuals_fm_snr.fits'), (science_data_all - modelconvolved)**2/sigma2, overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'residuals_fm_snr_and_term_extra.fits'), (science_data_all - modelconvolved)**2/sigma2 + np.log(sigma2) * mask2minimize , overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'params.fits'), params, overwrite=True)

            if do_robust_convolution:
                fits.writeto(os.path.join(intermediate_resultdir,'disk_model_Q_convolved.fits'),-Q_neg_convolved, overwrite=True)    
                fits.writeto(os.path.join(intermediate_resultdir,'disk_model_U_convolved.fits'),-U_neg_convolved, overwrite=True)     
    
            
        elif save_intermediate_results:
            dt =  datetime.now()  - startTime
            suffix = "_{:.2f}min_{:.0f}_{:.2f}".format(dt.seconds/60, Chisquare, Chisquare_red)

            fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm.fits'), science_data_all - modelconvolved, overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'residuals_fm_snr.fits'), (science_data_all - modelconvolved)**2/sigma2, overwrite=True)
            fits.writeto(os.path.join(detail_resultdir,'residuals_fm_snr_and_term_extra.fits'), (science_data_all - modelconvolved)**2/sigma2 + np.log(sigma2) * mask2minimize , overwrite=True)
            fits.writeto(os.path.join(intermediate_resultdir,'disk_model_convolved{}.fits'.format(suffix)), modelconvolved, overwrite=True)
            fits.writeto(os.path.join(intermediate_resultdir,'params{}.fits'.format(suffix)), params, overwrite=True)
            
    if display: 
        
        print(f'\nFor params')
        for i, name in enumerate(names):
            if convention_unit == 'MCMC':
                if name in ['inc', 'inclination']: params[i] = np.arccos(params[i])*180/np.pi
                if name in ['scaling', 'scaling1', 'scaling2']: params[i] = 10**params[i]
            print(f' {name} = {params[i]:.2f}')

        print(f'\n-> Chisquare = {Chisquare:.4e} i.e. {Chisquare:.0f}, Reduced chisquare = {Chisquare_red:.2f}')

    return Chisquare


def chisquare_logf_2obs_polar(params, dico = None):
    """ measure the Chisquare of the parameter set.
        create disk
        convolve by the PSF (psf is global)
        do the forward modeling (diskFM obj is global)
        nan out when it is out of the zone (zone mask is global)
        subctract from data and divide by noise (data and noise are global)

    Args:
        params: list of parameters of the MCMC

    Returns:
        Chisquare
    """
    startTime =  datetime.now() 

    # Access extra keyword arguments from kwargs
    display = dico.get('display', 0)
    nb_obs = dico.get('nb_obs', 1)
    type_obs_all = dico.get('type_obs_all', 'PROBLEM')
    #type_obs_all = dico.get('type_obs_all', 'PROBLEM')
    do_robust_convolution = dico.get('do_robust_convolution', 1)
    im_pa = dico.get('im_pa', 'PROBLEM')
    psf_all = dico.get('psf_all', 'PROBLEM')
    mask2minimize = dico.get('mask2minimize', 'PROBLEM')
    noise_all = dico.get('noise_all', 'PROBLEM')
    science_data_all = dico.get('science_data_all', 'PROBLEM')
    nresel = dico.get('nresel', 'PROBLEM')
    nparams = dico.get('nparams', 'PROBLEM')
    nparams_1obs = dico.get('nparams_1obs', 'PROBLEM')
    convention_unit = dico.get('convention_unit', 'PROBLEM')
    save_detail_results = dico.get('save_detail_results', False)
    save_intermediate_results = dico.get('save_intermediate_results', False)
    detail_resultdir = dico.get('detail_resultdir','None')
    intermediate_resultdir = dico.get('intermediate_resultdir','None')
    pa_array_all = dico.get('pa_array_all', 'PROBLEM')
    mask_rad = dico.get('mask_rad', 'MASK_RAD')
    nmodes = dico.get('nmodes', 'PROBLEM')
    pixscale_ins_all = dico.get('pixscale_ins_all', 'PROBLEM')
    names = dico.get('names', 'PROBLEM')

    # Check if some extra keyword arguments were effectively given
    if nb_obs>1 and type(type_obs_all) == type('PROBLEM'): raise ValueError('There is a problem with the value of type_obs_all.')
    if type(im_pa) == type(''): raise ValueError('There is a problem with the value of im_pa.')
    if type(psf_all) == type(''): raise ValueError('There is a problem with the value of psf_all.')
    if type(mask2minimize) == type(''): raise ValueError('There is a problem with the value of mask2minimize.')
    if type(noise_all) == type(''): raise ValueError('There is a problem with the value of noise_all.')
    if type(pa_array_all) == type(''): raise ValueError('There is a problem with the value of pa_array_all.')
    if type(science_data_all) == type(''): raise ValueError('There is a problem with the value of science_data_all.')
    if type(nresel) == type(''): raise ValueError('There is a problem with the value of nresel.')
    if type(nparams) == type(''): raise ValueError('There is a problem with the value of nparams.')
    if type(nparams_1obs) == type(''): raise ValueError('There is a problem with the value of nparams_1obs.')
    if type(mask_rad) == type(''): raise ValueError('There is a problem with the value of mask_rad.')
    if type(nmodes) == type(''): raise ValueError('There is a problem with the value of nmodes.')
    if convention_unit == 'PROBLEM': raise ValueError('There is a problem with the value of convention_unit.')
    if type(nb_obs) == type(''): raise ValueError('There is a problem with the value of nb_obs.')
    if type(names) == type(''): raise ValueError('There is a problem with the value of names.')

    #if display: print('In function chisquare_8params_2obs_polar() ')
    Chisquare_red_final = []
    params0, log_f0 = np.array([params[0],params[1],params[2],params[3],params[4]]), params[6]
    params1, log_f1 = np.array([params[0],params[1],params[2],params[3],params[5]]), params[7]
    
    ## Total intensity BBH ##
    i=0
    dico['disk_model_polar'] = False
    dico['pixscale_ins'] = pixscale_ins_all[i]
    dico['obs_id'] = '1'
    model = generate_disk_model(params, dico=dico)
            
    # Rotate the disk model for different angles and convolve it by the PSF
    modelconvolved = vip.fm.cube_inject_fakedisk(model, -pa_array_all[i], psf=psf_all[i])

    # Compute the residuals and the chisquare
    # Remove the disk from the observation
    CUBE_DIFF = (science_data_all[i] - modelconvolved)

    # Reduce the observation
    try:
        im_pca = vip.psfsub.pca_fullfr.pca(CUBE_DIFF, pa_array_all[i], ncomp=nmodes, mask_center_px=mask_rad, imlib='opencv', full_output=False)
    except: 
        raise ValueError(f'The PCA reduction did not converge. The disk parameters used are the following: {params}')


    sigma2 = (noise_all[i]**2 + np.exp(log_f0*2) * modelconvolved**2) 

    Chisquare0 = np.nansum( ( im_pca * mask2minimize ) **2  / sigma2 + np.log(sigma2) * mask2minimize ) # on fait attention de bien compter uniquement les régions dans le masque
    Chisquare_red = Chisquare0/(nresel-nparams_1obs-1)
    Chisquare_red_final.append(Chisquare_red)
            
    if save_intermediate_results:
        dt =  datetime.now()  - startTime
        suffix = "_{:.2f}min_{:.0f}_{:.2f}".format(dt.seconds/60, Chisquare0, Chisquare_red)
        modelconvolved0 = convolve_fft(model, psf_all[i], boundary='wrap')

        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_1{}.fits'.format(suffix)), im_pca, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_snr_1{}.fits'.format(suffix)), im_pca**2/sigma2, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_snr_and_term_extra_1{}.fits'.format(suffix)), im_pca**2/sigma2+np.log(sigma2), overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'disk_model_convolved_1{}.fits'.format(suffix)), modelconvolved0, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'params_1{}.fits'.format(suffix)), params, overwrite=True)

    if save_detail_results:
        modelconvolved0 = convolve_fft(model, psf_all[i], boundary='wrap')
        fits.writeto(os.path.join(detail_resultdir,'disk_model_1.fits'),model, overwrite=True)
        fits.writeto(os.path.join(detail_resultdir,'disk_model_convolved_1.fits'),modelconvolved0, overwrite=True)      
        fits.writeto(os.path.join(detail_resultdir,'residuals_fm_1.fits'), im_pca, overwrite=True)      
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_snr_1.fits'), im_pca**2/sigma2, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_snr_and_term_extra_1.fits'), im_pca**2/sigma2+np.log(sigma2), overwrite=True)
        fits.writeto(os.path.join(detail_resultdir,'params_1.fits'), params, overwrite=True)
            
          
    if display: 
        print(f'\nFor params (total intensity)')
        for i, name in enumerate(names):
            print(f' {name} = {params[i]:.2f}')

        print(f'\n-> Chisquare = {Chisquare0:.4e} i.e. {Chisquare0:.0f}, Reduced chisquare = {Chisquare_red:.2f}')
        print('\n(!) Final reduced chisquare =  {:.2f}\n'.format(Chisquare_red_final))
        if convention_unit != 'MCMC':
            print(f'\nFor params = \n radius = {params[0]:.3f} au \n PA = {params[1]:.3f} deg \n inc = {params[2]:.3f} deg \n g = {params[3]:.3f}  \n scaling1 = {params[4]:.0f} ADU \n logf1 = {params[6]:.2f} \n\n-> Chisquare = {Chisquare0:.4e} i.e. {Chisquare0:.0f}, Reduced chisquare = {Chisquare_red:.2f} (total intensity)\n')

        else:
            print(f'\nFor params = \n radius = {params[0]:.3f} au \n PA = {params[1]:.3f} deg \n inc = {(np.arccos(params[2])*180/np.pi):.3f} deg \n g = {params[3]:.3f} \n scaling1 = {(10**params[4]):.0f} ADU \n logf1 = {params[6]:.2f} \n\n-> Chisquare = {Chisquare0:.4e} i.e. {Chisquare0:.0f}, Reduced chisquare = {Chisquare_red:.2f} (total intensity) \n')
    
    ## Polar BBH ##
    i=1
    dico['disk_model_polar'] = True
    dico['pixscale_ins'] = pixscale_ins_all[i]
    dico['obs_id'] = 2
    model = generate_disk_model(params, dico=dico)

    if do_robust_convolution:
            # In particular important for close-in or asymmetric disks. See Heikamp & Keller 2019
            Q_neg = model*np.cos(2*im_pa)
            U_neg = model*np.sin(2*im_pa)
            Q_neg_convolved = convolve_fft(Q_neg, psf_all[i], boundary='wrap')#, mode='same')
            U_neg_convolved = convolve_fft(U_neg, psf_all[i], boundary='wrap')#, mode='same')
            modelconvolved = (Q_neg_convolved*np.cos(2*im_pa)+U_neg_convolved*np.sin(2*im_pa)) # corresponds to Qphi 
    
    else: modelconvolved = convolve_fft(model, psf_all[i], boundary='wrap')

    sigma2 = (noise_all[i]**2 + np.exp(log_f0*2) * modelconvolved**2) 
    res_all = (science_data_all[i] - modelconvolved) #(SCIENCE_DATA_MASK - modelconvolved0)
    Chisquare1 = np.nansum( ( res_all * mask2minimize ) **2  / sigma2 + np.log(sigma2) * mask2minimize ) # on fait attention de bien compter 
    Chisquare_red = Chisquare1/(nresel-nparams_1obs-1)
    Chisquare_red_final.append(Chisquare_red)

    if save_intermediate_results:
        suffix = "_{:.2f}min_{:.0f}_{:.2f}".format(dt.seconds/60, Chisquare1, Chisquare_red)
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_2{}.fits'.format(suffix)), res_all, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_snr_2{}.fits'.format(suffix)), res_all**2/sigma2, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_snr_and_term_extra_2{}.fits'.format(suffix)), res_all**2/sigma2+np.log(sigma2), overwrite=True) 
        fits.writeto(os.path.join(intermediate_resultdir,'disk_model_convolved_2{}.fits'.format(suffix)), modelconvolved, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'params_2{}.fits'.format(suffix)), params, overwrite=True)
        
        if do_robust_convolution:
            fits.writeto(os.path.join(intermediate_resultdir,'disk_model_Q_convolved{}.fits'.format(suffix)),-Q_neg_convolved, overwrite=True)      
            fits.writeto(os.path.join(intermediate_resultdir,'disk_model_U_convolved{}.fits'.format(suffix)),-U_neg_convolved, overwrite=True)      

    if save_detail_results:
        fits.writeto(os.path.join(detail_resultdir,'disk_model_2.fits'),model, overwrite=True)
        fits.writeto(os.path.join(detail_resultdir,'disk_model_convolved_2.fits'),modelconvolved, overwrite=True)      
        fits.writeto(os.path.join(detail_resultdir,'residuals_2.fits'), res_all, overwrite=True)    
        fits.writeto(os.path.join(detail_resultdir,'residuals_fm_snr_2.fits'), res_all**2/sigma2, overwrite=True)
        fits.writeto(os.path.join(intermediate_resultdir,'residuals_fm_snr_and_term_extra_2.fits'), res_all**2/sigma2+np.log(sigma2), overwrite=True) 
        fits.writeto(os.path.join(detail_resultdir,'params_2.fits'), params, overwrite=True)

        if do_robust_convolution:
            fits.writeto(os.path.join(detail_resultdir,'disk_model_Q_convolved.fits'),-Q_neg_convolved, overwrite=True)      
            fits.writeto(os.path.join(detail_resultdir,'disk_model_U_convolved.fits'),-U_neg_convolved, overwrite=True)      

    Chisquare_red_final = np.nanmean(Chisquare_red_final)

    if display: 
        print(f'\nFor params (polar)')
        for i, name in enumerate(names):
            print(f' {name} = {params[i]:.2f}')

        print(f'\n-> Chisquare = {Chisquare1:.4e} i.e. {Chisquare1:.0f}, Reduced chisquare = {Chisquare_red:.2f}')
        print('\n(!) Final reduced chisquare =  {:.2f}\n'.format(Chisquare_red_final))

    return Chisquare0+Chisquare1 #Chisquare_red_final