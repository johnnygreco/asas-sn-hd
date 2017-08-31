#!/usr/bin/env python 

import os
import numpy as np
import pandas as pd
from astropy.convolution import Tophat2DKernel
import schwimmbad
import mpi4py.MPI as MPI
import ashd
out_dir= '/Users/protostar/local_data/asas-sn-hd-io'
db_fn = os.path.join(out_dir, 'asas-sn-hd.db')


class Worker(object):

    def __init__(self, run_name):
        self.run_name = run_name
        self.butler = ashd.Butler()

    def work(self, coord):
        params = ashd.PipeParams()
        params.kernel = Tophat2DKernel(15)
        params.bh = 128
        params.bw = 128
        ra, dec = coord.ra.value, coord.dec.value
        try:
            pipe = ashd.ASHDPipe(ra, dec, params=params)
            pipe.logger.info('current image: '+pipe.image_label)
            pipe.detect()
            pipe.calc_auto_params()
            pipe.logger.info('writing to database')
            return pipe.image_label, pipe.sources
        except Exception as e:
            pipe.logger.error(e, ra, dec, 'failed')
            return None

    def callback(self, result):
        if result is not None:
            image_label, sources = result
            db_ingest = ashd.database.ASHDIngest(session, self.run_name)
            db_ingest.add_all(image_label, sources)

    def __call__(self, task):
        return self.work(task)


def main(pool, run_name='dev'):
    worker = Worker(run_name)
    coords = worker.butler.unique_coords
    for r in pool.map(worker, coords, callback=worker.callback):
        pass
    pool.close()


if __name__=='__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ncores", dest="n_cores", default=1, type=int)
    group.add_argument("--mpi", dest="mpi", default=False, action="store_true")
    args = parser.parse_args()

    if MPI.COMM_WORLD.Get_rank()==0:
        # open database session with master process
        engine = ashd.database.connect(db_fn)
        session = ashd.database.Session()

    pool = schwimmbad.choose_pool(mpi=args.mpi, processes=args.n_cores)
    main(pool)
