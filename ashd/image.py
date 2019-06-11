from __future__ import division, print_function

import numpy as np
from astropy import units as u
from astropy.wcs import WCS
#from .butler import Butler
from .utils import ndarray_byteswap

__all__ = ['ASHDImage']

class ASHDImage(object):

    def __init__(self, butler, ra=None, dec=None, unit=u.deg, image_fn=None):
        img_kws = dict(ra=ra, dec=dec, unit=unit, image_fn=image_fn)
        self.butler = butler
        self.header = self.butler.get_header(**img_kws)
        if image_fn is None:
            assert (ra is not None) and (dec is not None)
            self.image_fn = self.butler.get_image_fn(ra, dec, unit)
        else:
            self.image_fn = image_fn
        self.zpt = self.header['ZEROPT']
        self.wcs = WCS(self.header)
        self.data = ndarray_byteswap(self.butler.get_data(**img_kws))

    def sky_to_pix(self, sky_coord):
        if type(sky_coord[0]) not in (list, np.ndarray):
            ra, dec = sky_coord
            pix_coord = self.wcs.wcs_world2pix([[ra, dec]], 0)[0]
        else:
            pix_coord = self.wcs.wcs_world2pix(sky_coord, 0)
        return pix_coord

    def pix_to_sky(self, pix_coord):
        if type(pix_coord[0]) not in (list, np.ndarray):
            x, y= pix_coord
            sky_coord = self.wcs.wcs_pix2world([[x, y]], 0)[0]
        else:
            sky_coord = self.wcs.wcs_pix2world(pix_coord, 0)
        return sky_coord
