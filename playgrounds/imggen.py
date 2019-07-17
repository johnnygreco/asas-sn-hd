#%%
import ashd, sep
import ashd.pipelinev2 as pv2
from ashd.pipelinev2.reader import Reader

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import seaborn as sns

import math, os, multiprocessing, sys
from concurrent.futures import ProcessPoolExecutor

from astropy import visualization
from astropy.table import Table
from astropy.coordinates import SkyCoord

plt.rcParams["figure.figsize"] = [12, 12]

#%%
r = Reader('/home/me/Code/Research/results/algo1_run3')
d = r.data

#%%
norm = visualization.mpl_normalize.ImageNormalize(
    stretch=visualization.SqrtStretch())

#norm2 = 

def plotme(obj, rng=[10, 99], target=None, label=None):
    vmin, vmax = np.percentile(obj, rng)
    k = target if target != None else plt
    k.imshow(obj, cmap="Greys_r", norm=norm, vmin=vmin, vmax=vmax, origin='lower')
    if label: k.set(title=label)


#%%
b = ashd.Butler('/run/media/me/DATA/asas-sn-images')
sns.reset_orig()


#%%
xlength = lambda x: d['xmax'][x] - d['xmin'][x]

def patch(idx):
    x, y, a, b, theta = [d[n][idx] for n in ('x', 'y', 'a', 'b', 'theta')]
    e = patches.Ellipse(xy=(x, y),
                width=6*a,
                height=6*b,
                angle=theta * 180. / np.pi)
    e.set_facecolor('none')
    e.set_edgecolor('red')
    
    e2 = patches.Rectangle(xy=(d['xmin'][idx], d['ymax'][idx]),
                           width=xlength(idx),
                           height=2,
                          label="Test")
    return (e, e2)

def get_frame(idx):
    return b.get_image(ra=d['ra'][idx], dec = d['dec'][idx])

def writeout(idx, out=None):
    try:
        fig, ax = plt.subplots()
        plotme(get_frame(idx).data, target=ax)
        for i in patch(idx): ax.add_artist(i)
        ax.text(d['xmin'][idx], d['ymax'][idx] + 5, f"{(xlength(idx) * 7.8):.2f}\"", color="orange", fontsize=16)
        ax.set_xlim(d['xmin'][idx] - 20, d['xmax'][idx] + 20)
        ax.set_ylim(d['ymin'][idx] - 20, d['ymax'][idx] + 20)
        ax.set(xlabel=', '.join([f"{d[x][idx]:.2f}" for x in ('ra', 'dec')]))
        plt.savefig(out if out else f"scanlations/{idx}.png", bbox_inches='tight')
        print("Done", idx)
    except:
        print(sys.exc_info())


#%%
#pool = multiprocessing.Pool(12)
with ProcessPoolExecutor(max_workers=10) as ppe:
    #writeout(i)
    #pool.apply_async(writeout, args=(i))
    ppe.map(writeout, range(len(d)))
