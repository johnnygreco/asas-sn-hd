from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import scipy.ndimage as ndi

__all__ = ['rmedian', 'make_cutout', 'exp_kern']


def _ring(r_inner, r_outer, dtype=np.int, invert=False):
    """
    Generate a 2D ring footprint.
    Paramters
    ---------
    r_inner : int
        The inner radius of ring in pixels.
    r_outer : int
        The outer radius of ring in pixels.
    dtype : data type, optional
        The data type of the output array
    invert : bool, optional
        If True, invert the ring kernel (i.e., 1 <--> 0).
    Returns
    -------
    fp : 2D ndarray
        The ring footprint with 1's in the 
        annulus and 0's everywhere else.
    """
    assert r_outer >= r_inner, 'must have r_outer >= r_inner'
    x = np.arange(-int(r_outer), int(r_outer)+1)
    r = np.sqrt(x**2 + x[:,None]**2)
    annulus = (r>r_inner) & (r<=r_outer)
    if invert:
        annulus = ~annulus
    r[annulus] = 1
    r[~annulus] = 0
    fp = r.astype(dtype)
    return fp


def rmedian(image, r_inner, r_outer, **kwargs):
    """
    Median filter image with a ring footprint. This
    function produces results similar to the IRAF 
    task of the same name (except this is much faster). 
    Parameters
    ----------
    image : ndarray 
       Original image data. 
    r_inner : int
        The inner radius of the ring in pixels.
    r_outer : int
        The outer radius of the ring in pixels.
    Returns
    -------
    filtered_data : ndarray
        Ring filtered image.
    """
    fp = _ring(r_inner, r_outer, **kwargs)
    filtered_data = ndi.median_filter(image, footprint=fp)
    return filtered_data


def make_cutout(data, coord, unit='deg', header=None, 
           size=301, write=None):
    """
    Generate a postage stamp from a fits image.

    Parameters
    ----------
    data : 2D ndarray
        The data from the fits file.
    coord : tuple
        The central coordinates for the cutout. If 
        header is None, then unit is pixels, else
        it is ra and dec in degrees.
    unit : astropy.units.Unit or str, optional
        Unit of coordinates
    header : Fits header, optional
        The fits header, which must have WCS info.
    size : int, array-like, optional
        The size of the cutout array along each axis.
        If an integer is given, will get a square. 
    write : string, optional
        If not None, save the cutout to this 
        file name.

    Returns
    -------
    cutout : Cutout2D object, if write is None
       A cutout object containing the 2D cutout data 
       array and the updated WCS.
    """
    from astropy.nddata import Cutout2D
    from astropy.coordinates import SkyCoord

    if header is None:
        cutout = Cutout2D(data, coord, size)
    else:
        from astropy import wcs
        w = wcs.WCS(header)
        coord = SkyCoord(coord[0], coord[1], frame='icrs', unit=unit) 
        cutout = Cutout2D(data, coord, size, wcs=w)

    if write is None:
        return cutout
    else:
        from astropy.io import fits
        header = cutout.wcs.to_header() if header is not None else None
        fits.writeto(write, cutout.data, header, clobber=True)


def exp_kern(alpha, size, norm_array=False, mode='center', factor=10):
    """
    Generate 2D, radially symmetric exponential kernal for sextractor. 
    The kernels are discretized using `astropy.convolution.discretize_model`.
    Parameters
    ----------
    alpha : float
        The scale length of the exponential.
    size : odd int
        Number of pixel in x & y directions.
    norm_array : bool, optional
        If True, normalize the kern array. 
    mode : str, optional
        One of the following discretization modes: 
        'center', 'oversample', 'linear_interp', 
        or 'integrate'. See astropy docs for details. 
    factor : float or int
        Factor of oversampling. 
    Returns
    -------
    kern : 2D ndarray, if (return_fn=False)
        The convolution kernel. 
    kern, fn, comment : ndarray, string, string (if return_fn=True)
        The kernel, file name, and the comment
        for the file.
    Notes
    -----
    The kernel will be normalized by sextractor by 
    default, and the non-normalized files are a bit 
    cleaner due to less leading zeros. 
    """
    assert size%2!=0, 'ERROR: size must be odd'
    from astropy.convolution import discretize_model

    x_range = (-(int(size) - 1) // 2, (int(size) - 1) // 2 + 1)
    model = lambda x, y: np.exp(-np.sqrt(x**2 + y**2)/alpha)
    kern = discretize_model(model, x_range, x_range, mode=mode, factor=factor)

    if norm_array:
        kern /= kern.sum()
    
    return kern
