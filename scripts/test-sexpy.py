#!/usr/bin/env python 

import os
from astropy.io import fits
import sexpy
import ashd 

pixscale = 7.8
local_io = os.environ.get('LOCAL_DATA')
sexdir = os.path.join(local_io, 'asas-sn-hugs-io/sex')
configdir = os.path.join(sexdir, 'config')
sexin = os.path.join(sexdir, 'in')
sexout = os.path.join(sexdir, 'out')

datadir = '/Users/protostar/Dropbox/projects/data/asas-sn-images'
run_fn = os.path.join(datadir, 'F0025-10_1599.be.fits')


config = dict(DETECT_THRESH=1.5, 
              DEBLEND_NTHRESH=6, 
              DEBLEND_MINCONT=0.008,
              PHOT_APERTURES='2,3,6')
params = ['MAG_APER('+str(i+1)+')' for i in range(3)]


sw = sexpy.SexWrapper(config=config, 
                      sexin=sexin, 
                      sexout=sexout, 
                      configdir=configdir,
                      params=params)

img = fits.getdata(run_fn)
head = fits.getheader(run_fn)
img_rm = ashd.rmedian(img, 2.0, 4.0)
new_fn = sw.get_indir('img_ring_filtered.fits')
fits.writeto(new_fn, img_rm,  header=head, overwrite=True)

#new_fn = new_fn+','+run_fn

sw.run(new_fn)

cat = sexpy.read_cat(sw.get_outdir('sex.cat'))
sexpy.cat_to_ds9reg(cat, outfile=sw.get_outdir('sex.reg'))
