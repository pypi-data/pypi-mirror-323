#from import_functions_generic import *

'''
compute_im_pa_grid() (version of 2025-01-15)

author: Célia Desgrange
'''

import numpy as np

def compute_im_rad_grid(im, center='n//2-0.5', xc=None, yc=None, display=1):
    '''
    Returns a 2D radius grid with the same shape than the input image 'im'. The unit is in pixels.

    Inputs:
        .'im' (2D array): only the shape of 'im' will be used, not its values.

        (optional)

        .'center' (string): indicates where is the center of the image. Three options: 'n//2-0.5', 'n//2-1' or 'n//2', 'coordinates_are_given'.
            Default value: center='n//2-0.5'. 
                Examples: 
                    For an even image, this means the center is between the four centered-pixels.
                    For an odd image, this means the center is the pixel at the center.
            Other possible values: 'n//2-1' or 'n//2' (but only if the image is even) or 'coordinates_are_given'.
            If 'coordinates_are_given', specify the parameters 'xc' and 'yc'.
            (!) Important: Assumption: count starts at 0.

        .'xc' (float): The coordinate in the abscisse axis of the center of the image.

        .'yc' (float): The coordinate in the abscisse axis of the center of the image.

        .'display' (boolean or binary value): prints information if sets to True or 1 (which is the default value)

    Output:
        .'zs' (2D array): each pixel has for value its distance to the center of the image. The unit is in pixels. The shape of 'zs' is the same than the input array 'im'.

    ---------
    Examples:
        .compute_im_rad_grid(np.zeros((4,4)), center='center') returns

            array( [[2.82842712, 2.10818511, 2.10818511, 2.82842712],
                    [2.10818511, 0.94280904, 0.94280904, 2.10818511],
                    [2.10818511, 0.94280904, 0.94280904, 2.10818511],
                    [2.82842712, 2.10818511, 2.10818511, 2.82842712]])

        .compute_im_rad_grid(np.zeros((4,4)), center='n//2') returns 

            array( [[2.82842712, 2.23606798, 2.        , 2.23606798],
                    [2.23606798, 1.41421356, 1.        , 1.41421356],
                    [2.        , 1.        , 0.        , 1.        ],
                    [2.23606798, 1.41421356, 1.        , 1.41421356]])

        .compute_im_rad_grid(np.zeros((4,4)), center='n//2-1')

            array( [[1.41421356, 1.        , 1.41421356, 2.23606798],
                    [1.        , 0.        , 1.        , 2.        ],
                    [1.41421356, 1.        , 1.41421356, 2.23606798],
                    [2.23606798, 2.        , 2.23606798, 2.82842712]])

        .compute_im_rad_grid(np.zeros((n,n)), 'center') returns

            array( [[1.41421356, 1.        , 1.41421356],
                    [1.        , 0.        , 1.        ],
                    [1.41421356, 1.        , 1.41421356]])
    '''
    if display: print("\n(Compute 2D radius grid for an even or odd image) \n (!) Don't forget to select the good option for the center of the image.")

    nx = np.shape(im)[1]
    ny = np.shape(im)[0]

    if nx % 2 == 0  and ny % 2 == 0: even_or_odd = 'even'
    elif nx % 2 == 1  and ny % 2 == 1: even_or_odd = 'odd'
    else: raise ValueError(f"The image should be in both axis either even or odd. However, its shape is {np.shape(im)}.")

    if center == 'coordinates_are_given': 
        xend, yend = nx-xc, ny-yc
        xbeg, ybeg = -xc, -yc
        
        x,y = np.arange(xbeg,xend,1), np.arange(ybeg, yend,1)
        xs,ys = np.meshgrid(x, y, sparse=True)
        zs = np.sqrt(xs**2 + ys**2)

    elif even_or_odd == 'even':
        if center == 'n//2-0.5': x,y = np.linspace(-nx//2,nx//2,nx), np.linspace(-ny//2,ny//2,ny)
        elif center == 'n//2': x,y = np.linspace(-nx//2,nx//2-1,nx), np.linspace(-ny//2,ny//2-1,ny)
        elif center == 'n//2-1': x,y = np.linspace(-nx//2+1,nx//2,nx), np.linspace(-ny//2+1,ny//2,ny)
        else: raise ValueError(f"If the image has an even shape, the value of 'center' should be 'n//2-0.5', 'n//2' or 'n//2-1' and not {center}.")

    elif even_or_odd == 'odd':
        if center == 'n//2-0.5': x,y = np.linspace(-nx//2+1,nx//2,nx), np.linspace(-ny//2+1,ny//2,ny)
        else: raise ValueError(f"If the image has an odd shape, the value of 'center' should be 'center' and not {center}.")

    xs,ys = np.meshgrid(x, y, sparse=True)
    zs = np.sqrt(xs**2 + ys**2)
    return zs



def compute_im_pa_grid(im, center='n//2', xc=None, yc=None, return_unit='deg', counterclockwise=True, display=0):
    '''
    Returns a 2D-array whose values are position angles from the top to the right (so counterclockwise) by default.

    Inputs:
        .'im' (2D array): only the shape of 'im' will be used, not its values.

        (optional)

        .'center' (string): indicates where is the center of the image. Three options: 'n//2-0.5', 'n//2-1' or 'n//2', 'coordinates_are_given'.
            Default value: center='n//2-0.5'. 
                Examples: 
                    For an even image, this means the center is between the four centered-pixels.
                    For an odd image, this means the center is the pixel at the center.
            Other possible values: 'n//2-1' or 'n//2' (but only if the image is even) or 'coordinates_are_given'.
            If 'coordinates_are_given', specify the parameters 'xc' and 'yc'.
            (!) Important: Assumption: count starts at 0.

        .'xc' (float): The coordinate in the abscisse axis of the center of the image. Default value: None.

        .'yc' (float): The coordinate in the abscisse axis of the center of the image. Default value: None.

        .'counterclockwise' (boolean or binary): if set to True (default value), position angles increase from the top to the right. If set to False, position angles increase from the top to the left.

        .'return_unit' (string): The unit of the pixels.  Default value: 'deg' (in degree).

        .'display' (boolean or binary value): prints information if sets to True or 1 (which is the default value)

    Output:
        .'thetas' (2D array): each pixel has for value its position angle from the North (up) of the image towards the East (left; astro convention) of the image. The unit is in degrees if 'return_unit' is set to 'deg', otherwise in radians. The shape of 'thetas' is the same than the input array 'im'.
    '''
    if display: print("\n(Compute 2D position angle grid for an even or odd image) \n (!) Don't forget to select the good option for the center of the image.")

    nx, ny = np.shape(im)[1], np.shape(im)[0]

    if nx % 2 == 0  and ny % 2 == 0: even_or_odd = 'even'
    elif nx % 2 == 1  and ny % 2 == 1: even_or_odd = 'odd'
    else: raise ValueError(f"The image should be in both axis either even or odd. However, its shape is {np.shape(im)}.")

    if center == 'coordinates_are_given': 
        xend, yend = nx-xc, ny-yc
        xbeg, ybeg = -xc, -yc
        
        x,y = np.arange(xbeg,xend,1), np.arange(ybeg, yend,1)
        xs,ys = np.meshgrid(x, y, sparse=True)
        zs = np.sqrt(xs**2 + ys**2)

    elif even_or_odd == 'even':
        if center == 'n//2-0.5': x,y = np.linspace(-nx//2,nx//2,nx), np.linspace(-ny//2,ny//2,ny)
        elif center == 'n//2': x,y = np.linspace(-nx//2,nx//2-1,nx), np.linspace(-ny//2,ny//2-1,ny)
        elif center == 'n//2-1': x,y = np.linspace(-nx//2+1,nx//2,nx), np.linspace(-ny//2+1,ny//2,ny)
        else: raise ValueError(f"If the image has an even shape, the value of 'center' should be 'n//2-0.5', 'n//2' or 'n//2-1' and not {center}.")

    elif even_or_odd == 'odd':
        if center == 'n//2-0.5': x,y = np.linspace(-nx//2+1,nx//2,nx), np.linspace(-ny//2+1,ny//2,ny)
        else: raise ValueError(f"If the image has an odd shape, the value of 'center' should be 'center' and not {center}.")

    xs,ys  = np.meshgrid(x, y, sparse=True)
    zs     = np.sqrt(xs**2 + ys**2)
    thetas = 2*np.arctan( xs/(ys+zs)) + np.pi 
    thetas[np.isnan(thetas)] = 0

   
    thetas = thetas[::-1,:] 
    if not counterclockwise: thetas = thetas[:,::-1] 

    if return_unit == 'deg': return thetas*180/np.pi
    else: return thetas
    


def compute_limdet_map_ann(res_map, dr, alpha=2, center='n//2-0.5', xc=None, yc=None, display=1):
    '''
    Returns the detection limit 2D map. This map is computed by annular noise estimation with slippery annulus. Calls the function compute im_rad_grid() to derive the distance (in pixel) of each pixel to the center of the image.

    Inputs:
        .'res_map' (2D-array): residual map
        
        .'dr' (float): width of the annulus for which the detection limit is computed

        (optional)

        .'alpha' (float): factor to consider bigger annulus to derive the noise. The annulus is located in an interval [-dr-alpha; dr+alpha] at a given radius. The goal is to have a smoother transition between annuli.
        
        .'center' (string): indicates where is the center of the image. Three options: 'n//2-0.5', 'n//2-1' or 'n//2', 'coordinates_are_given'.
            Default value: center='n//2-0.5'. 
                Examples: 
                    For an even image, this means the center is between the four centered-pixels.
                    For an odd image, this means the center is the pixel at the center.
            Other possible values: 'n//2-1' or 'n//2' (but only if the image is even) or 'coordinates_are_given'.
            If 'coordinates_are_given', specify the parameters 'xc' and 'yc'.
            (!) Important: Assumption: count starts at 0.
            Additional information is available in the docstring of the function compute_im_rad_grid()

        .'xc' (float): The coordinate in the abscisse axis of the center of the image.

        .'yc' (float): The coordinate in the abscisse axis of the center of the image.

        .'display' (boolean or binary value): prints information if sets to True or 1 (which is the default value)

    Output:
        .'im_noise' (2D-array): detection limit map. 
    '''

    t0 = time.time()
    if display: print("\n(Computing the detection limit map by using the 1D-annulus method)")
    h, w = np.shape(res_map)
    noise_tot, noise_ann = [], []

    im_noise, im_nan = np.zeros((h,w)), np.empty((h,w)), 
    im_radius_grid   = compute_im_rad_grid(res_map, center=center, xc=None, yc=None, display=display)
    im_nan[:] = np.nan
    rad       = alpha

    # Loop until the radius of the annulus considered is bigger than the size of the image divided by two
    while rad < w//2 * 1.45: #w//2 - alpha - dr :
        # One annulus is considered
        rad += dr
        cond_annulus_large = np.logical_and(im_radius_grid >= rad-alpha, rad + dr + alpha >= im_radius_grid)
        cond_annulus_thin  = np.logical_and(im_radius_grid >= rad, rad + dr >= im_radius_grid)
        im_annulus = np.where(cond_annulus_large, res_map, im_nan)
        # the noise over the annulus is computed
        noise_annulus = np.nanstd(im_annulus)
        # and the image is set at this noise for this given annulus
        im_noise[cond_annulus_thin] = noise_annulus
        rad += dr
    if display: print("Took {} seconds".format(time.time()-t0))

    return im_noise


# Below to update, and the docstrings


def compute_mean_map_ann(im, dr, alpha=0, add_input_im_rad=0, im_rad=None, center='n//2-0.5', xc=None, yc=None, display=0):
    '''
    Compute the averaged mean 2D map by annular estimation with slippery annulus.
    Use the function compute im_rad_grid() to derive the distance (in pixel) of each
    pixel to the center of the image.

    Inputs:
        .'im' (2D-array): image
        .'dr' (float): width of the annulus for which the detection limit is computed
        (optional)
        .'alpha' (float): factor to consider bigger annulus to derive the noise
            Goal: have smoother transition between annuli
        .'add_input_im_rad' (boolean): input corresponding to the 2D radius grid provided
            (if parameter set to 1) or not (parameter set to 0, default value)
        .'im_rad' (2D-array): None (if add_input_im_rad == 0) or a 2D radius grid with the
            same shape than the input image 'im' (if add_input_im_rad == 1)
        .'display' (boolean):
            Default value: 0 (False) i.e. do not display details/information

    Output:
        .'im_noise' (2D-array): detection limit map
    '''
    t0 = time.time()
    if display: print("\nComputing the standard deviation limit map by using the 1D-annulus method")
    h, w = np.shape(im)

    im_noise, im_nan, = np.zeros((h,w)), np.empty((h,w))
    if add_input_im_rad : im_radius_grid = im_rad
    else : im_radius_grid = compute_im_rad_grid(res_map, center=center, xc=None, yc=None, display=display)

    im_nan[:] = np.NaN
    rad = 0

    # Until the annulus is smaller than the size of the image
    while rad < w//2 * 1.45 : # 1.45 slightly bigger than sqrt(2) to be sure to cover all the field of view and not only a circle of radius r
        # One annulus is considered
        cond_annulus_large = np.logical_and(im_radius_grid >= rad-alpha, rad + dr + alpha >= im_radius_grid)
        cond_annulus_thin  = np.logical_and(im_radius_grid >= rad, rad + dr >= im_radius_grid)
        im_annulus = np.where(cond_annulus_large, im, im_nan)
        # the noise over the annulus is computed
        noise_annulus = np.nanmean(im_annulus)
        # and the image is set at this noise for this given annulus
        im_noise[cond_annulus_thin] = noise_annulus
        rad += dr
    if display: print("-> took {} seconds".format(time.time()-t0))
    return im_noise


def compute_mad_map_ann(im, dr, alpha=0, add_input_im_rad=0, im_rad=None, display=0):
    '''
    Compute the mean absolute deviation 2D map by annular noise estimation with slippery annulus.
    Use the function compute im_rad_grid() to derive the distance (in pixel) of each
    pixel to the center of the image.

    Inputs:
        .'im' (2D-array): image
        .'dr' (float): width of the annulus for which the detection limit is computed
        (optional)
        .'alpha' (float): factor to consider bigger annulus to derive the noise
            Goal: have smoother transition between annuli
        .'add_input_im_rad' (boolean): input corresponding to the 2D radius grid provided
            (if parameter set to 1) or not (parameter set to 0, default value)
        .'im_rad' (2D-array): None (if add_input_im_rad == 0) or a 2D radius grid with the
            same shape than the input image 'im' (if add_input_im_rad == 1)
        .'display' (boolean):
            Default value: 0 (False) i.e. do not display details/information

    Output:
        .'im_noise' (2D-array): detection limit map
    '''
    t0 = time.time()
    if display: print("\nComputing the standard deviation limit map by using the 1D-annulus method")
    h, w = np.shape(im)
    noise_tot, noise_ann = [], []

    im_noise, im_nan, = np.zeros((h,w)), np.empty((h,w))
    if add_input_im_rad : im_radius_grid = im_rad
    else : im_radius_grid = compute_im_rad_grid(im)

    im_nan[:] = np.NaN
    rad, x0,y0 = 0, w//2+1, h//2+1

    # Until the annulus is smaller than the size of the image
    while rad < w//2 * 1.45 : # 1.45 slightly bigger than sqrt(2) to be sure to cover all the field of view and not only a circle of radius r
        # One annulus is considered
        cond_annulus_large = np.logical_and(im_radius_grid >= rad-alpha, rad + dr + alpha >= im_radius_grid)
        cond_annulus_thin  = np.logical_and(im_radius_grid >= rad, rad + dr >= im_radius_grid)
        im_annulus = np.where(cond_annulus_large, im, im_nan)
        # the noise over the annulus is computed
        noise_annulus = molmap.compute_mad(im_annulus)
        # and the image is set at this noise for this given annulus
        im_noise[cond_annulus_thin] = noise_annulus
        rad += dr
    if display: print("-> took {:.3f} seconds.".format(time.time()-t0))
    return im_noise


def compute_std_map_ann(im, dr, alpha=0, add_input_im_rad=0, im_rad=None, display=0):
    '''
    Compute the standard deviation 2D map by annular noise estimation with slippery annulus.
    Use the function compute im_rad_grid() to derive the distance (in pixel) of each
    pixel to the center of the image.

    Inputs:
        .'im' (2D-array): image
        .'dr' (float): width of the annulus for which the detection limit is computed
        (optional)
        .'alpha' (float): factor to consider bigger annulus to derive the noise
            Goal: have smoother transition between annuli
        .'add_input_im_rad' (boolean): input corresponding to the 2D radius grid provided
            (if parameter set to 1) or not (parameter set to 0, default value)
        .'im_rad' (2D-array): None (if add_input_im_rad == 0) or a 2D radius grid with the
            same shape than the input image 'im' (if add_input_im_rad == 1)
        .'display' (boolean):
            Default value: 0 (False) i.e. do not display details/information

    Output:
        .'im_noise' (2D-array): detection limit map
    '''
    t0 = time.time()
    if display: print("\nComputing the standard deviation limit map by using the 1D-annulus method")
    h, w = np.shape(im)
    noise_tot, noise_ann = [], []

    im_noise, im_nan, = np.zeros((h,w)), np.empty((h,w))
    if add_input_im_rad : im_radius_grid = im_rad
    else : im_radius_grid = compute_im_rad_grid(im)

    im_nan[:] = np.NaN
    rad, x0,y0 = 0, w//2+1, h//2+1

    # Until the annulus is smaller than the size of the image
    while rad < w//2 * 1.45 : # 1.45 slightly bigger than sqrt(2) to be sure to cover all the field of view and not only a circle of radius r
        # One annulus is considered
        cond_annulus_large = np.logical_and(im_radius_grid >= rad-alpha, rad + dr + alpha >= im_radius_grid)
        cond_annulus_thin  = np.logical_and(im_radius_grid >= rad, rad + dr >= im_radius_grid)
        im_annulus = np.where(cond_annulus_large, im, im_nan)
        # the noise over the annulus is computed
        noise_annulus = np.nanstd(im_annulus)
        # and the image is set at this noise for this given annulus
        im_noise[cond_annulus_thin] = noise_annulus
        rad += dr
    if display: print("-> took {} seconds".format(time.time()-t0))
    return im_noise


def compute_std_cube_spatially_annuli(cube, dr, alpha=0, display=0, display_level2=0):
    '''
    Compute a 3D standard deviation cube. For each frame of the cube, the standard
    deviation is computed spatially in rings centered around the star which is
    assumed to be at the center of the image.

    Note: le bruit sur chaque anneau ne pourrait pas être calculé en utilant VIP? frame_basic_stats
    '''
    if display:
        print('In function compute_std_cube_spatially_annuli()')
        t0 = time.time()

    nim = np.shape(cube)[0]
    nxy = np.shape(cube)[1]
    im_rad = compute_im_rad_grid(cube[0])
    cube_std = np.zeros((nim,nxy,nxy))
    # loop over the images (on the spectral or temporal dimension for instance):
    for i, im in enumerate(cube):
        cube_std[i] = compute_std_map_ann(im, dr, alpha=alpha, add_input_im_rad=1, im_rad=im_rad, display=display_level2)

    if display: print("-> took {:.1f} seconds".format(time.time()-t0))
    return cube_std

def compute_std_cube_spatially_aperture(cube, rad=2, display=0):
    '''
    Compute a 3D standard deviation cube by considering noise in an aperture around each pixel:
    loop over the images and each coordinates (time-consuming).
    Relevant to consider the photon noise of a putative fake planet.

    Inputs (...)
    '''

    if display:
        print('In function compute_std_cube_spatially_aperture()')
        t0 = time.time()

    nim = np.shape(cube)[0]
    nxy = np.shape(cube)[1]
    cube_std = np.zeros(np.shape(cube))

    # Option (1)
    for iw in range(nim):
        for ix in range(nxy):
            for iy in range(nxy):
                mean, cube_std[iw,iy,ix], median, tot = frame_basic_stats(cube[iw], radius=rad, xy=(ix,iy), full_output=True, plot=False)

    if display: print("-> took {:.1f} seconds".format(time.time()-t0))
    return cube_std




def compute_std_cube_spatially(cube, rad, dr, alpha=0, use_empty_obs=0, cube_annuli=None, consider_photon_noise=0, cube_noise_photon=0, saving_dir='', writeo=False, display=0):
    '''
    Compute a 3D standard deviation cube by considering the noise both from annuli
    and aperture around each pixel.
    '''
    #cube_std_aperture = compute_std_cube_spatially_aperture(cube=cube, rad=rad, display=display)
    if use_empty_obs : cube=cube_annuli ; print('Use a cube without fake planet injected to derive the noise on the annuli.')
    #else:  print('Use a cube with the fake planet injected to derive the noise on the annuli.')
    cube_std_annuli = compute_std_cube_spatially_annuli(cube=cube, dr=dr, alpha=alpha, display=display)

    if consider_photon_noise:
        print('The spatial noise is estimated by regarding two components: annulus-wise standard deviation of the values centered on the star location, and the photon noise at each location.')
        cube_std = np.sqrt(cube_std_annuli**2+np.abs(cube_noise_photon))#cube_std_aperture**2)
    else:
        print('The spatial noise is estimated only by regarding rings centered on the star location.')
        cube_std = np.abs(cube_std_annuli)

    if writeo :
        fits.writeto(saving_dir+'std_cube_spatial_annuli.fits', cube_std_annuli, overwrite=True)
        fits.writeto(saving_dir+'std_cube_spatial.fits', cube_std, overwrite=True)

        if consider_photon_noise:
            fits.writeto(saving_dir+'std_cube_spatial_aperture.fits', np.abs(cube_noise_photon), overwrite=True)
    return cube_std



def rad_profile(im, center, mode='std', pixscale=1, dr=1, skip_pix=None):
    '''
    Assumption: center at n//2-1 i.e. between the four central pixel (for even image)

    Function useful to reproduce the Figure 3 from Hoeijmakers et al. (2018).
    '''
    if skip_pix == None: skip_pix=3

    if mode == 'std':
        im = compute_std_map_ann(im,dr=dr)
        #profile = (im_std[skip_pix+int(center):,int(center)]+im_std[skip_pix+int(center):,int(center+1)])/2
        profile = im[skip_pix+int(center):,int(center)]
        separations = np.arange(skip_pix,len(im)//2.,1)

    elif mode == 'mad':
        im = compute_mad_map_ann(im,dr=dr)
        #profile = (im_std[skip_pix+int(center):,int(center)]+im_std[skip_pix+int(center):,int(center+1)])/2
        profile = im[skip_pix+int(center):,int(center)]
        separations = np.arange(skip_pix,len(im)//2.,1)

    elif mode == 'mean':
        im = compute_mean_map_ann(im,dr=dr)
        profile = im[skip_pix+int(center):,int(center)]
        separations = np.arange(skip_pix,len(im)//2.,1)
    else: print('Precise a mode available, e.g. std or mean. Here the mode given is {}'.format(mode))

    return profile, separations*pixscale

