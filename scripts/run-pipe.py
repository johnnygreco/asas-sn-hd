#!/usr/bin/env python 

import os
import numpy as np
import pandas as pd
from astropy.convolution import Tophat2DKernel
import ashd
DATA_DIR= '/scr/depot0/jgreco/asas-sn-stacks'
OUT_DIR = '/scr/depot0/jgreco/asas-sn-hd-io'
db_fn = os.path.join(OUT_DIR, 'asas-sn-hd.db')
engine = ashd.database.connect(db_fn)
session = ashd.database.Session()

files = [os.path.join(DATA_DIR, fn) for fn\
         in os.listdir(DATA_DIR) if fn[0]=='F']

for num, fn in enumerate(files):
    print('now serving file #', num)

    params = ashd.PipeParams()
    params.kernel = Tophat2DKernel(15)
    params.bh = 128
    params.bw = 128
    params.data_dir =  DATA_DIR

    try:
        pipe = ashd.ASHDPipe(image_fn=fn, params=params)
        pipe.detect()
        pipe.calc_auto_params()
        pipe.write_to_db(session)
    except Exception as e:
        print(e, fn, 'failed')
