from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from .image import ASHDImage

class Butler(object):
    """
    Fetch ASAS-SN stacked images. 
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.files = [file for file in os.listdir(self.data_dir) if file[-4:]=='fits']
        ra_vals = []
        dec_vals = []
        for f in self.files:
            _ra = int(f[1:5])
            if _ra > 2400:
                _ra = _ra - 2400
            _ra = str(_ra).zfill(4)
            ra_vals.append(_ra[:2]+':'+_ra[2:]+':00')
            dec_vals.append(f[5:8])
        self.fn_coords = SkyCoord(ra_vals, dec_vals, unit=(u.hourangle, u.deg))
        ra_vals = self.fn_coords.ra.value 
        dec_vals = self.fn_coords.dec.value 
        df = pd.DataFrame(dict(ra=ra_vals, dec=dec_vals))
        df.drop_duplicates(inplace=True)
        self.unique_coords = SkyCoord(
            df.ra.values, df.dec.values, unit=(u.hourangle, u.deg))
        
    def get_image_fn(self, ra, dec=None, unit='deg'):
        #ra can also be the entire SkyCoord here
        coord = SkyCoord(ra, dec, unit=unit) if dec != None else ra
        seps = self.fn_coords.separation(coord)
        fn_coord = self.fn_coords[seps.argmin()].to_string('hmsdms').split()
        fn_ra = ''.join(re.split('[a-z]', fn_coord[0])[:2])
        fn_dec = re.split('[a-z]', fn_coord[1])[0]
        prefix = f'F{fn_ra}{fn_dec}_'
        fn = [f for f in self.files if prefix in f]
        if len(fn)>1:
            sig = []
            for f in fn:
                sig.append(self.get_sb_sig(image_fn=f))
            fn = fn[np.argmax(sig)]
        else:
            fn = fn[0]
        return os.path.join(self.data_dir, fn)
    
    def get_image(self, ra, dec=None, unit='deg'):
        return ASHDImage(self, ra=ra, dec=dec)

    def get_hdulist(self, ra=None, dec=None, unit='deg', image_fn=None):
        fn = image_fn if image_fn else self.get_image_fn(ra, dec, unit=unit)
        return fits.open(fn)

    def get_data(self, ra=None, dec=None, unit='deg', image_fn=None):
        fn = image_fn if image_fn else self.get_image_fn(ra, dec, unit=unit)
        return fits.getdata(fn)

    def get_header(self, ra=None, dec=None, unit='deg', image_fn=None):
        fn = image_fn if image_fn else self.get_image_fn(ra, dec, unit=unit)
        return fits.getheader(fn)

    #Returns np.nan if the object has no SB_SIG
    def get_sb_sig(self, ra=None, dec=None, unit='deg', image_fn=None):
        fn = image_fn if image_fn else self.get_image_fn(ra, dec, unit=unit)
        head = fits.getheader(os.path.join(self.data_dir, fn))
        return head.get('SB_SIG', np.nan)
