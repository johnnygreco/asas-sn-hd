from __future__ import division, print_function

import numpy as np
from astropy import units as u
from astropy.wcs import WCS
from .butler import Butler, data_dir
from .utils import ndarray_byteswap

__all__ = ['ASHDImage']

class ASHDImage(object):

    def __init__(self, ra, dec, unit=u.deg, data_dir=data_dir):
        self.butler = Butler(data_dir)
        self.header = self.butler.get_header(ra, dec, unit)
        self.image_fn = self.butler.get_image_fn(ra, dec, unit)
        self.zpt = self.header['ZEROPT']
        self.wcs = WCS(self.header)
        self.data = ndarray_byteswap(self.butler.get_data(ra, dec, unit))

    def sky_to_pix(self, sky_coord):
        if type(sky_coord[0])==float or type(sky_coord[0])==np.float64:
            ra, dec = sky_coord
            pix_coord = self.wcs.wcs_world2pix([[ra, dec]], 0)[0]
        else:
            pix_coord = self.wcs.wcs_world2pix(sky_coord, 0)
        return pix_coord
