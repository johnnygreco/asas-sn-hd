#%%

import astropy
import numpy as np

from ashd import Butler

from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord

from scipy import interpolate, signal

import os, glob, sys, argparse

import sqlite3, multiprocessing, logging

from common import get_objs
from global_vals import *

# algo1 can be replaced with with algo2 (or whichever one you want to use)
import algo1 as algo

# Some convenience functions
def unwrap(coord): return (coord.ra.deg, coord.dec.deg)
def objhash(obj): return np.base_repr(abs(hash(obj.tostring())), 36).lower()

# the main processing method; called in each process
def process(coord, butler, logstr='', **kwargs):
    c = unwrap(coord)
    logging.debug(f"[Process {multiprocessing.current_process().pid}] [Coordinate {c}] {logstr}")
    img = butler.get_image(*c)
    #dsub = img.data.byteswap().newbyteorder()
    objects, *_ = get_objs(img.data)
    lbgs = algo.find_lbg(objects, img.data)
    out = []
    for obj in lbgs:
        coord = img.pix_to_sky([obj['x'], obj['y']])
        # create a cutout
        zoomed_img = img.data[obj['ymin']:obj['ymax'], obj['xmin']:obj['xmax']]
        logging.info(f"At {coord}: {str(obj)}; Hash: {objhash(obj)}")
        out.append((coord, obj, zoomed_img))
    return (out, img.header)
        
# takes the output of `process` and writes it to the sqlite table and creates image files of the cutouts
def callback(params):
    global objCount, args
    objlist, header = params
    for i in objlist:
        coord, obj, zoomed = i
        uid = np.base_repr(objCount, 36)
        h = objhash(obj)
        logging.debug(f"Writing {coord} with id {uid} of hash {h}")
        #cur = conn.cursor()
        c.execute("insert into findings values (?, ?, ?, ?, ?)",
                    (uid, h, coord[0], coord[1], obj.tostring()))
        hdu = fits.PrimaryHDU(zoomed)
        hdu.header = header
        hdu.writeto(os.path.join(args.output_dir, f"{uid}.fits"))
        objCount += 1

#%%
if __name__ == "__main__":
    logging.basicConfig(format=f"[%(asctime)s][%(levelname)s] %(message)s", level=logging.DEBUG)

    run = len(glob.glob("./out*.db"))

    parser = argparse.ArgumentParser(description="Try and find dwarf galaxies from the asas-sn data.")

    parser.add_argument('--max-tries', type=int, default=MAX_TRIES,
                        help="we're looking at the top `MAX_TRIES` number of found objects")
    parser.add_argument('--max-findings', type=int, default=MAX_FINDINGS,
                        help="out of those objects above, how many `MAX_FINDINGS` should we return?")
    parser.add_argument('--source', type=str,
                        help="source directory for the ASAS-SN stacks")
    parser.add_argument('--processes', type=int, default=4,
                        help="how many processes to execute on")
    parser.add_argument('--output-dir', type=str, default=f'./out{run}',
                        help="the output directory to dump")
    parser.add_argument('--max-processed', type=int, default=None,
                        help="if you have a large source directory, we will only take the first `MAX_PROCESSED` images")

    args = parser.parse_args()

    logging.info(f"Initializing with arguments: {args}")

    if not os.path.exists(args.output_dir): os.mkdir(args.output_dir)
    butler = Butler(args.source)

    args = parser.parse_args()
    logging.info(f"Running with {args.processes} processes. Process {multiprocessing.current_process().pid} is the main process.")
    conn = sqlite3.connect(os.path.join(args.output_dir, "db"), check_same_thread=False)
    c = conn.cursor()
    c.execute("create table findings (id text, hash text, ra real, dec real, properties text)")

    pool = multiprocessing.Pool(args.processes)
    cnt = args.max_processed if (args.max_processed and args.max_processed < len(butler.unique_coords)) else len(butler.unique_coords)

    # a counter for the total list of objects that only exists in the main process
    objCount = 0

    logging.info(f"Processing {cnt} coordinates.")

    for i in range(cnt):
        coord = butler.unique_coords[i]
        pool.apply_async(process, args=(coord, butler, f"Index {i + 1}/{cnt}"), callback=callback)
    pool.close()
    pool.join()
    
    conn.commit()
    conn.close()
    logging.info(f"{objCount} objects found.")
