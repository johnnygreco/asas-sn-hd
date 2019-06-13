#%%
#%matplotlib notebook

import photutils, astropy
from photutils import datasets
from astropy.modeling.functional_models import Sersic2D

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches

from astropy import visualization, convolution, stats

import ashd

from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord

import sep, argparse

from scipy import interpolate, signal

#%%
def get_img_data(coord, file_path, butler=None):
    coord = SkyCoord(coord)
    return ashd.ASHDImage(ra=coord.ra.deg, dec=coord.dec.deg)
    #imgn = butler.get_image_fn(ra=coord.ra.deg,dec=coord.dec.deg)
    #img = fits.open(imgn)
    #return img[0].data


def get_objs(data):
    datab = data.byteswap().newbyteorder()
    background = sep.Background(datab)
    dsub = datab - background
    objects = sep.extract(dsub, 1.5, err=background.globalrms)
    return (objects, dsub, background)

def cut_corners(objlist, thresh=30, size=[2048, 2048]):
    for i in objlist:
        x = i['x']; y = i['y']
        if not (x < thresh and y < thresh) and not (x > (size[0] - thresh) and y < thresh):
            if not (x < thresh and y > (size[1] - thresh)) and not (x > (size[0] - thresh) and y > (size[1] - thresh)):
                yield i

def find_lbg_old(objects, maxtries=10, percentiles=(0,90), corners=False):
    if not corners: objects = np.array(list(cut_corners(objects, thresh=500)))

    avgsb = np.mean(objects['cflux'] / objects['npix'])

    brightsort = sorted(objects, key=lambda x: x['cflux'] / x['npix']); cnt = len(brightsort)
    largest = sorted(brightsort[cnt * percentiles[0] // 100 : cnt * percentiles[1] // 100],
                    key=lambda x: x['npix'], reverse=True)[0:maxtries+1]
    for obj in largest:
        sb = obj['cflux'] / obj['npix']
        if sb < avgsb:
            return obj
    return None

def find_lbg(objects, data, maxtries=-1, percentiles=(0,90), corners=False):
    if maxtries < 0: maxtries = objects.size
    if not corners: objects = np.array(list(cut_corners(objects, thresh=500)))
    
    largest = sorted(objects, key = lambda x: x['npix'], reverse=True)[0:maxtries+1]
    for obj in largest:
        if is_lbg(obj, data): return obj
    return None

def is_lbg(obj, data, default=[30, 2030], extend=30, sigma=1000):
    subset, smoothed = datavals(obj, data, default, extend, sigma)
    
    m = np.mean(smoothed)
    maxval = m + np.std(smoothed)
    mid = smoothed[smoothed.size // 2]
    p25 = smoothed[smoothed.size // 4] - smoothed[(smoothed.size // 4) - 1]
    p75 = smoothed[smoothed.size * 3 // 4] - smoothed[(smoothed.size * 3 // 4) - 1]
    return mid > maxval and p25 > 0 and p75 < m

def datavals(obj, data, default, extend, sigma):
    xmin = int(obj['xmin']) - extend
    xmin = xmin if xmin > default[0] else default[0]
    xmax = int(obj['xmax']) + extend
    xmax = xmax if xmax < default[1] else default[1]
    
    subset = data[int(obj['y']), xmin:xmax]
    #ash = np.arcsinh(subset)
    smoothed = signal.cspline1d(subset, sigma)
    
    return (subset, smoothed)

#def process_object(obj):
    

#%%
def main():
    parser = argparse.ArgumentParser(description="Try and find dwarf galaxies from the asas-sn data given ra and dec.")
    parser.add_argument('--max-tries', type=int, default=10)
    parser.add_argument('--source', type=str)
    parser.add_argument('coordinates', type=str)

    args = parser.parse_args()

    #butler = ashd.Butler(args.source)

    data = get_img_data(args.coordinates, args.source)
    objects, *_ = get_objs(data)
    print(find_lbg(objects, data))

if __name__ == "__main__": main()