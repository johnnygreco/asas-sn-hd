from global_vals import *
from common import cut_corners
import numpy as np

# this algorithm revolves around taking the largest objects and measuring their flux
# those with a lower average flux while still being large are our best LSB candidates
def find_lbg(objects, data, **kwargs):
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