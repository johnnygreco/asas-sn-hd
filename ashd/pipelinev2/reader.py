import sqlite3, os
import numpy as np
import pandas as pd
from astropy.io import fits

SEP_DTYPE = [('thresh', '<f8'), ('npix', '<i8'), ('tnpix', '<i8'), ('xmin', '<i8'), ('xmax', '<i8'), ('ymin', '<i8'),
    ('ymax', '<i8'), ('x', '<f8'), ('y', '<f8'), ('x2', '<f8'), ('y2', '<f8'), ('xy', '<f8'), ('errx2', '<f8'),
    ('erry2', '<f8'), ('errxy', '<f8'), ('a', '<f8'), ('b', '<f8'), ('theta', '<f8'), ('cxx', '<f8'), ('cyy', '<f8'),
    ('cxy', '<f8'), ('cflux', '<f8'), ('flux', '<f8'), ('cpeak', '<f8'), ('peak', '<f8'), ('xcpeak', '<i8'), ('ycpeak', '<i8'),
    ('xpeak', '<i8'), ('ypeak', '<i8'), ('flag', '<i8')]

SQL_DTYPE=[("id", "<i8"), ("ra", "<f8"), ("dec", "<f8")]

class Reader:
    def __init__(self, target, autoload = True):
        self.target = target
        db = os.path.join(self.target, 'db')
        #print(f"sqlite:///{db}", os.path.exists(db))
        self.conn = sqlite3.Connection(db)
        if autoload: self.load()
    
    def load(self):
        c = self.conn.cursor()
        self.extra_data = []
        for row in c.execute("select count(*) from findings"): np_table = np.empty(row[0], dtype=SEP_DTYPE)
        
        pos = 0
        #ra = []; dec = []
        for row in c.execute("select * from findings"):
            self.extra_data.append(row[0:4])
            np_table[pos] = np.fromstring(row[4], dtype=SEP_DTYPE)
            pos += 1
        self.data = pd.DataFrame(np_table)
        self.data['ra'] = [i[2] for i in self.extra_data]
        self.data['dec'] = [i[3] for i in self.extra_data]
        
    
    def get_img(self, id):
        fname = id
        if type(id) == int:
            fname = np.base_repr(id, 36)
        return fits.open(os.path.join(self.target, f"{fname}.fits"))[0]

        