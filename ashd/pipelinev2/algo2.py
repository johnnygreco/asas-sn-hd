from global_vals import *
from common import cut_corners
import numpy as np
from scipy import signal

# this algo revolves around finding objects wherein some form gradient/sersic can be found
# basically, how do you avoid star clusters
def find_lbg(objects, data, **kwargs):
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
    _, smoothed = datavals(obj, data, default, extend, sigma)
    
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