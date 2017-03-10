from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
IMDIR = '/Users/protostar/Dropbox/projects/data/asas-sn-images'

class Butler(object):
    """
    Fetch ASAS-SN stacked images. 
    """

    def __init__(self, imdir=IMDIR):
        self.imdir = imdir
        self.files = [fn for fn in os.listdir(self.imdir) if fn[-4:]=='fits']
        ra_vals = []
        dec_vals = []
        for fn in self.files:
            _ra = int(fn[1:5])
            if _ra > 2400:
                _ra = _ra - 2400
            _ra = str(_ra).zfill(4)
            ra_vals.append(_ra[:2]+':'+_ra[2:]+':00')
            dec_vals.append(fn[5:8])
        self.fn_coords = SkyCoord(ra_vals, dec_vals, unit=(u.hourangle, u.deg))

    def get_image_fn(self, ra, dec, unit=u.deg):
        coord = SkyCoord(ra, dec, unit=unit)
        seps = self.fn_coords.separation(coord)
        fn_coord = self.fn_coords[seps.argmin()].to_string('hmsdms').split()
        fn_ra = ''.join(re.split('[a-z]', fn_coord[0])[:2])
        fn_dec = re.split('[a-z]', fn_coord[1])[0]
        prefix = 'F{}{}_'.format(fn_ra, fn_dec)
        fn = [f for f in self.files if prefix in f]
        if len(fn)>1:
            sig = []
            for f in fn:
                sig.append(self.get_sb_sig(fn=f))
            fn = fn[np.argmin(sig)]
        else:
            fn = fn[0]
        return os.path.join(self.imdir, fn)

    def get_hdulist(self, ra=None, dec=None, unit=u.deg, fn=None):
        fn = fn if fn else self.get_image_fn(ra, dec, unit=u.deg)
        return fits.open(fn)

    def get_data(self, ra=None, dec=None, unit=u.deg, fn=None):
        fn = fn if fn else self.get_image_fn(ra, dec, unit=u.deg)
        return fits.getdata(fn)

    def get_header(self, ra=None, dec=None, unit=u.deg, fn=None):
        fn = fn if fn else self.get_image_fn(ra, dec, unit=u.deg)
        return fits.getheader(fn)

    def get_sb_sig(self, ra=None, dec=None, unit=u.deg, fn=None):
        fn = fn if fn else self.get_image_fn(ra, dec, unit=u.deg)
        head = fits.getheader(os.path.join(self.imdir, fn))
        return head['SB_SIG']
