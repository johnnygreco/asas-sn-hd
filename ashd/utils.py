import os
import numpy as np

__all__ = ['pixscale', 'project_dir', 'ndarray_byteswap', 
           'isiterable', 'get_logger']

pixscale = 7.8 # arcsec/pixel
project_dir = os.path.dirname(os.path.dirname(__file__))


def ndarray_byteswap(arr):
    """
    If array is in big-endian byte order (as astropy.io.fits
    always returns), swap to little-endian for SEP.
    """
    if arr.dtype.byteorder=='>':
        arr = arr.byteswap().newbyteorder()
    return arr


def isiterable(obj):
    """
    Returns `True` if the given object is iterable.

    Taken from astropy/utils/misc.py
    """
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def get_logger(level='debug', label='',
	       log_file_dir=os.path.join(project_dir, 'logs')):
    import logging
    import logzero
    from logzero import logger
    log_fn = os.path.join(log_file_dir, 'ashd.log')
    logzero.loglevel(getattr(logging, level.upper()))
    logzero.logfile(log_fn)
    formatter = logging.Formatter(
        '%(module)s %(lineno)d | %(asctime)s | '+\
        label+' | %(levelname)s: %(message)s')
    logzero.formatter(formatter)
    return logger
