#!/usr/bin/env python 

import os
from astropy.table import Table
from astropy.io import fits
import sexpy
import asshugs

dwarfs = Table.read('/Users/protostar/Downloads/nearby-dwarfs.fits')
dwarfs.rename_column('_RAJ2000', 'ra')
dwarfs.rename_column('_DEJ2000', 'dec')

pixscale = 7.8
butler = asshugs.Butler()
local_io = os.environ.get('LOCAL_DATA')
sexdir = os.path.join(local_io, 'asas-sn-hugs-io/sex')
configdir = os.path.join(sexdir, 'config')
sexin = os.path.join(sexdir, 'in')
sexout = os.path.join(sexdir, 'out')
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

names = ['Leo II', 'Phoenix', 'Cetus', 
         'Andromeda III', 'Andromeda II', 'IC 10']

for name in names:
    ra, dec = dwarfs[dwarfs['Name']==name]['ra', 'dec'][0]
    run_fn = butler.get_image_fn(ra, dec)
    img = fits.getdata(run_fn)
    head = fits.getheader(run_fn)
    img_ring = asshugs.rmedian(img, 2.0, 4.0)
    label = name.replace(' ', '-')
    new_fn = sw.get_indir(label+'-ring-filtered.fits')
    fits.writeto(new_fn, img_ring,  header=head, overwrite=True)
    cat_fn = sw.get_outdir(label+'-sex.cat')
    sw.run(new_fn, cat=cat_fn)
    cat = sexpy.read_cat(cat_fn)
    sexpy.cat_to_ds9reg(cat, outfile=sw.get_outdir(label+'-sex.reg'))
