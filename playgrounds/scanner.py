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

import sqlite3, multiprocessing, logging

MAX_TRIES = 10
MAX_FINDINGS = 3

SEP_DTYPE = [('thresh', '<f8'), ('npix', '<i8'), ('tnpix', '<i8'), ('xmin', '<i8'), ('xmax', '<i8'), ('ymin', '<i8'),
    ('ymax', '<i8'), ('x', '<f8'), ('y', '<f8'), ('x2', '<f8'), ('y2', '<f8'), ('xy', '<f8'), ('errx2', '<f8'),
    ('erry2', '<f8'), ('errxy', '<f8'), ('a', '<f8'), ('b', '<f8'), ('theta', '<f8'), ('cxx', '<f8'), ('cyy', '<f8'),
    ('cxy', '<f8'), ('cflux', '<f8'), ('flux', '<f8'), ('cpeak', '<f8'), ('peak', '<f8'), ('xcpeak', '<i8'), ('ycpeak', '<i8'),
    ('xpeak', '<i8'), ('ypeak', '<i8'), ('flag', '<i8')]

logging.basicConfig(format=f"[%(asctime)s][%(levelname)s] %(message)s", level=logging.DEBUG)

def unwrap(coord): return (coord.ra.deg, coord.dec.deg)
def objhash(obj): return np.base_repr(abs(hash(obj.tostring())), 36).lower()

#%%
def get_objs(datab):
    #datab = data.byteswap().newbyteorder()
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
                    key=lambda x: x['npix'], reverse=True)[0:kwargs.get('maxtries', MAX_TRIES)]
    found = 0; maxfindings = kwargs.get('maxfindings', MAX_FINDINGS)
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
    found = 0; maxfindings = kwargs.get('maxfindings', MAX_FINDINGS)
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

def process(coord, butler, logstr='', **kwargs):
    c = unwrap(coord)
    logging.debug(f"[Process {multiprocessing.current_process().pid}] [Coordinate {c}] {logstr}")
    img = butler.get_image(*c)
    #dsub = img.data.byteswap().newbyteorder()
    objects, *_ = get_objs(img.data)
    lbgs = find_lbg_v1(objects, img.data)
    out = []
    for obj in lbgs:
        coord = img.pix_to_sky([obj['x'], obj['y']])
        zoomed_img = img.data[obj['ymin']:obj['ymax'], obj['xmin']:obj['xmax']]
        logging.info(f"At {coord}: {str(obj)}; Hash: {objhash(obj)}")
        out.append((coord, obj, zoomed_img))
    return out
        

def callback(objlist):
    global objCount, args
    for i in objlist:
        coord, obj, zoomed = i
        uid = np.base_repr(objCount, 36)
        h = objhash(obj)
        logging.debug(f"Writing {coord} with id {uid} of hash {h}")
        #cur = conn.cursor()
        c.execute("insert into findings values (?, ?, ?, ?, ?)",
                    (uid, h, coord[0], coord[1], obj.tostring()))
        hdu = fits.PrimaryHDU(zoomed)
        hdu.writeto(os.path.join(args.output_dir, f"{uid}.fits"))
        objCount += 1

#%%
if __name__ == "__main__":
    run = len(glob.glob("./out*.db"))

    parser = argparse.ArgumentParser(description="Try and find dwarf galaxies from the asas-sn data.")
    parser.add_argument('--max-tries', type=int, default=MAX_TRIES)
    parser.add_argument('--max-findings', type=int, default=MAX_FINDINGS)
    parser.add_argument('--source', type=str)
    parser.add_argument('--processes', type=int, default=4)
    parser.add_argument('--output-dir', type=str, default=f'./out{run}')
    parser.add_argument('--max-processed', type=int, default=None)

    args = parser.parse_args()

    logging.info(f"Initializing with arguments: {args}")

    if not os.path.exists(args.output_dir): os.mkdir(args.output_dir)
    butler = ashd.Butler(args.source)

    args = parser.parse_args()
    logging.info(f"Running with {args.processes} processes. Process {multiprocessing.current_process().pid} is the main process.")
    conn = sqlite3.connect(os.path.join(args.output_dir, "db"), check_same_thread=False)
    c = conn.cursor()
    c.execute("create table findings (id text, hash text, ra real, dec real, properties text)")

    pool = multiprocessing.Pool(args.processes)
    cnt = args.max_processed if (args.max_processed and args.max_processed < len(butler.unique_coords)) else len(butler.unique_coords)
    objCount = 0

    logging.info(f"Processing {cnt} coordinates.")

    for i in range(cnt):
        coord = butler.unique_coords[i]
        pool.apply_async(process, args=(coord, butler), callback=callback)
    pool.close()
    pool.join()
    
    conn.commit()
    conn.close()
    logging.info(f"{objCount} objects found.")