from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sep

def calc_auto_params(data, src, zpt):
    x, y, a, b, theta = src['x'], src['y'], src['a'], src['b'], src['theta']
    kronrad, krflag = sep.kron_radius(data, x, y, a, b, theta, 6.0)
    flux, fluxerr, flag = sep.sum_ellipse(
	data, x, y, a, b, theta, 2.5*kronrad, subpix=1)
    flag |= krflag  # combine flags into 'flag'
    mag_auto = zpt - 2.5*np.log10(flux)    
    r, flag = sep.flux_radius(data, x, y, 6.*a, 0.5, normflux=flux, subpix=5)
    src['mag_auto'] = mag_auto
    src['flux_auto'] = flux
    src['flux_radius'] = r

def detect_sources(image):
    pass



