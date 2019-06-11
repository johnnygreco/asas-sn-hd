from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from astropy import units as u
from astropy.visualization import ZScaleInterval
from astropy.io import fits
from . import imutils
from . import utils
from .butler import Butler

__all__ = ['Display']

class Display(object):
    """
    Helper class for displaying stacked asas-sn images.
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.butler = Butler(data_dir)
        self._ds9 = None

    @property
    def ds9(self):
        if self._ds9 is None:
            import pyds9
            self._ds9 = pyds9.DS9()
        return self._ds9

    def ds9_view(self, ra, dec, unit=u.deg, plot_coord=False):
        """
        Display nearest image to (ra, dec) using ds9.

        Parameters
        ----------
        ra : float
            Right Ascension 
        dec : float
            Declination 
        unit : astropy.units.Unit, optional
            Unit of coordinates
        """ 
        img_fn = self.butler.get_image_fn(ra, dec, unit)
        self.ds9.set('file '+img_fn)
        if plot_coord:
            self.ds9.set('regions', 'icrs; circle({},{},30") # color=red '.\
                     format(ra, dec))

    def ds9_cutout(self, ra, dec, unit=u.deg, size=300, ell_par=[]):
        """
        Display cutout image using ds9.
        Parameters
        ----------
        ra : float
            Right Ascension 
        dec : float
            Declination 
        unit : astropy.units.Unit or str, optional
            Unit of coordinates
	size : int, array-like, optional
	    The size (in pixels) of the cutout array along each axis.
	    If an integer is given, will get a square. 
        """
        hdu = self.butler.get_hdulist(ra, dec, unit)[0]
        header = hdu.header
        data = hdu.data
        cutout = imutils.make_cutout(data, (ra, dec), unit=unit,    
                                     header=header, size=size)
        hdulist = fits.HDUList([fits.PrimaryHDU(
                                data=cutout.data, 
                                header=cutout.wcs.to_header(relax=False))])
        self.ds9.set_pyfits(hdulist)

        if ell_par:
            'ell_par = x, y, a, b, theta, [color]'
            if len(ell_par)==5:
                ell_par.append('cyan')
            ell_par[2] *= utils.pixscale
            ell_par[3] *= utils.pixscale
            txt = 'icrs; ellipse({},{},{}",{}",{}) # color={}'
            self.ds9.set('regions', txt.format(*ell_par))


    def mpl_view(self, ra=None, dec=None, unit=u.deg, pipe=None, 
                 stretch='zscale', cmap='gray_r',
                 figsize=(8, 8), imshow_kw={}):
        """
        Display image nearest image to (ra, dec) using matplotlib.
        Must give ra & dec --or-- a pipeline object.

        Parameters
        ----------
        ra : float
            Right Ascension 
        dec : float
            Declination 
        unit : astropy.units.Unit, optional
            Unit of coordinates
        pipe : ashd.pipeline.ASHDPipe, optional
            Pipeline object, which has an image attribute
        stretch: str, optional
            Image stretch (zscale, ...)
        cmap : str, optional
            matplotlib colormap
        figsize : tuple, optional
            Figure size
        imshow_kw : dict, optional
            Keyword args for imshow

        Returns 
        -------
        fig : matplotlib.figure.Figure
            matplotlib figure 
        ax : matplotlib.axes._subplots.AxesSubplot
            matplotlib axis
        """
        if pipe is None:
            assert (ra is not None) and (dec is not None)
            data = self.butler.get_data(ra, dec, unit)
        else:
            data = pipe.original_data

        if stretch == 'zscale':
            zscale = ZScaleInterval()
            vmin, vmax = zscale.get_limits(data)
        elif scale == 'log':
            # TODO 
            # implement this 
            pass

        fig, ax = plt.subplots(figsize=figsize, 
                               subplot_kw=dict(xticks=[], yticks=[]))
        ax.imshow(data, vmin=vmin, vmax=vmax, origin='lower', 
                  cmap=cmap, **imshow_kw)

        return fig, ax

    def mpl_view_sources(self, pipe, plot_coord=False, condition=None, 
                         save_fn=None, **kwargs):
        fig, ax = self.mpl_view(pipe=pipe, **kwargs)

        if plot_coord:
            pix_x, pix_y = pipe.image.sky_to_pix(pipe.coord)
            ax.plot(pix_x, pix_y, marker='o', mec='c', 
                    ms=25, mfc='none', mew=2)

	# plot an ellipse for each object
        sources = pipe.sources.copy()
        if condition is not None:
            sources = sources[condition]
        for _, src in sources.iterrows():
            e = Ellipse(xy=(src.x, src.y),
			width=6*src.a,
			height=6*src.b,
			angle=src.theta * 180. / np.pi)
            e.set_facecolor('none')
            e.set_edgecolor('red')
            ax.add_artist(e)
        if save_fn is not None:
            fig.savefig(save_fn)
            plt.close(fig)

