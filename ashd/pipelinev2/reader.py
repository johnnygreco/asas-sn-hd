import sqlite3

SEP_DTYPE = [('thresh', '<f8'), ('npix', '<i8'), ('tnpix', '<i8'), ('xmin', '<i8'), ('xmax', '<i8'), ('ymin', '<i8'),
    ('ymax', '<i8'), ('x', '<f8'), ('y', '<f8'), ('x2', '<f8'), ('y2', '<f8'), ('xy', '<f8'), ('errx2', '<f8'),
    ('erry2', '<f8'), ('errxy', '<f8'), ('a', '<f8'), ('b', '<f8'), ('theta', '<f8'), ('cxx', '<f8'), ('cyy', '<f8'),
    ('cxy', '<f8'), ('cflux', '<f8'), ('flux', '<f8'), ('cpeak', '<f8'), ('peak', '<f8'), ('xcpeak', '<i8'), ('ycpeak', '<i8'),
    ('xpeak', '<i8'), ('ypeak', '<i8'), ('flag', '<i8')]

class Reader:
    def __init__(self, target, autoload = True):
        self.target = target
        self.conn = sqlite3.connect(f"sqlite:///{target}/db")
        self.c = self.conn.cursor()
    
    @property
    def size(self): pass

    def iter(self): pass
