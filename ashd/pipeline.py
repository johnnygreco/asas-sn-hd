from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
from astropy import units as u
import sep
from .imutils import rmedian
from .image import ASHDImage
from .pipeparams import PipeParams
from . import utils

__all__ = ['ASHDPipe']

class ASHDPipe(object):
    
    def __init__(self, ra, dec, unit=u.deg, params=None):
        self.params = params if params else PipeParams()
        self.logger = utils.get_logger(level=self.params.log_level)
        self.logger.info('fetching image nearest to ra, dec = {:.4f}, {:.4f}'.\
                         format(ra, dec)) 
        self.image = ASHDImage(ra, dec, unit)
        self.data = self.image.data.copy()
        self.coord = [ra, dec]
        self._display = None

    @property
    def original_data(self):
        return self.image.data

    @property
    def display(self):
        if self._display is None:
            from .display import Display
            self._display = Display()
        return self._display

    def ring_filter(self, r_inner=3.0, r_outer=4.0):
        self.logger.info(
            'smoothing image with ring filter with r_in = {} and r_out = {}'.\
            format(r_inner, r_outer))
        self.data = rmedian(self.data, r_inner, r_outer)

    def detect(self):
        if self.params.do_ring_filter:
            self.ring_filter(self.params.r_inner, self.params.r_outer)
        self.logger.info('measuring and subtracting background')
        bkg = sep.Background(self.data, **self.params.sep_back_kws)
        self.data_sub = self.data - bkg
        self.logger.info('detecting sources')
        self.sources =  sep.extract(
            self.data_sub, err=bkg.globalrms, **self.params.sep_extract_kws)
        self.sources = pd.DataFrame(self.sources)
        
    def calc_auto_params(self):
        cols = ['x', 'y', 'a', 'b', 'theta']
        x, y, a, b, theta = self.sources.loc[:, cols].values.T
        kronrad, krflag = sep.kron_radius(
            self.data_sub, x, y, a, b, theta, 6.0)
        flux, fluxerr, flag = sep.sum_ellipse(
            self.data_sub, x, y, a, b, theta, 2.5*kronrad, subpix=1)
        flag |= krflag  # combine flags into 'flag'
        mag_auto = self.image.zpt - 2.5*np.log10(flux)    
        r, flag = sep.flux_radius(
            self.data_sub, x, y, 6.*a, 0.5, normflux=flux, subpix=5)
        self.sources['mag_auto'] = mag_auto
        self.sources['flux_auto'] = flux
        self.sources['flux_radius'] = r

    def display_sources(self, plot_coord=False, **kwargs):
        self.logger.info('displaying sources with mpl')
        self.display.mpl_view_sources(
            pipe=self, plot_coord=plot_coord, **kwargs)

    def display_ds9(self, plot_coord=False):
        self.logger.info('displaying image with ds9')
        self.display.ds9_view(self.coord[0], self.coord[1], 
                              plot_coord=plot_coord)
