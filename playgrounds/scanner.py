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

import os, glob, sys

import sqlite3

#%%
def get_img_data(coord, file_path, butler=None):
    coord = SkyCoord(coord)
    return 
    #return ashd.ASHDImage(ra=coord.ra.deg, dec=coord.dec.deg)
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

def find_lbg_v1(objects, data, **kwargs):
    if not kwargs.get('corners', False): objects = np.array(list(cut_corners(objects, thresh=500)))
    percentiles = kwargs.get('percentiles', [10,99])

    avgsb = np.mean(objects['cflux'] / objects['npix'])

    brightsort = sorted(objects, key=lambda x: x['cflux'] / x['npix']); cnt = len(brightsort)
    largest = sorted(brightsort[cnt * percentiles[0] // 100 : cnt * percentiles[1] // 100],
                    key=lambda x: x['npix'], reverse=True)[0:kwargs.get('maxtries', 10)]
    found = 0; maxfindings = kwargs.get('maxfindings', 2)
    for obj in largest:
        sb = obj['cflux'] / obj['npix']
        if sb < avgsb:
            found += 1
            yield obj
            if found > maxfindings: break
    #return None

def find_lbg_v2(objects, data, **kwargs):
    maxtries = kwargs.get('maxtries', objects.size)
    if not kwargs.get('corners', False): objects = np.array(list(cut_corners(objects, thresh=500)))
    
    largest = sorted(objects, key = lambda x: x['npix'], reverse=True)[0:maxtries]
    found = 0; maxfindings = kwargs.get('maxfindings', 2)
    for obj in largest:
        if is_lbg(obj, data):
            found += 1
            yield obj
            if found > maxfindings: break
    #return None

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
    parser = argparse.ArgumentParser(description="Try and find dwarf galaxies from the asas-sn data.")
    parser.add_argument('--max-tries', type=int, default=10)
    parser.add_argument('--max-per-img', type=int, default=2)
    parser.add_argument('--source', type=str)
    #parser.add_argument('coordinates', type=str)

    run = len(glob.glob("./out*.db"))
    os.mkdir(f"./out{run}")

    args = parser.parse_args()
    conn = sqlite3.connect(f"out{run}.db")
    c = conn.cursor()
    c.execute("create table findings (id text, ra real, dec real, properties text)")

    butler = ashd.Butler(args.source)
    count = 0
    for i in butler.fn_coords:
        try:
            img = butler.get_image(i.ra.deg, i.dec.deg)
        except:
            print(sys.exc_info()[1])
            print(f"Reader barfed on coordinate {str(i)}. Skipping...")
            continue
        dsub = img.data.byteswap().newbyteorder()
        objects, *_ = get_objs(dsub)
        lbgs = find_lbg_v1(objects, dsub, maxtries=args.max_tries, maxfindings=args.max_per_img)
        for obj in lbgs:
            print(obj)
            uid = np.base_repr(count, 36)
            coord = img.pix_to_sky([obj['x'], obj['y']])
            #print(coord)
            zoomed_img = img.data[obj['ymin']:obj['ymax'], obj['xmin']:obj['xmax']]
            c.execute("insert into findings values (?, ?, ?, ?)",
                        (uid, coord[0], coord[1], str(obj)))
            hdu = fits.PrimaryHDU(zoomed_img)
            hdu.writeto(f"./out{run}/{uid}.fits")
            count += 1
    
    conn.commit()
    conn.close()
    print(count, "objects found.")





if __name__ == "__main__": main()