from astropy.stats import gaussian_fwhm_to_sigma
from astropy.convolution import Gaussian2DKernel

class PipeParams(object):
    """
    Class to hold all the pipline parameters.
    """

    def __init__(self):

        self.log_level = 'info'
        self.data_dir = '/Users/protostar/Dropbox/projects/data/asas-sn-images'
        
        # sep.Background parameters
        self.bw = 64
        self.bh = 64
        self.fw = 3
        self.fh = 3
        self.fthresh = 0.0

        # sep.extract parameters
        self.thresh = 1.5
        self.minarea = 80
        self.deblend_nthresh = 32
        self.deblend_cont = 0.005
        self.clean = True
        self.clean_param = 1.0
        self.segmentation_map = False
        self.filter_type = 'conv'

        # smoothing kernel
        size = 31
        self.gauss_fwhm = 5.0
        sigma = gaussian_fwhm_to_sigma*self.gauss_fwhm
        self.kernel = Gaussian2DKernel(sigma, x_size=size, y_size=size)

        # ring filter parameters
        self.do_ring_filter = True
        self.r_inner = 5.0
        self.r_outer = 8.0

    @property
    def sep_back_kws(self):
        kws = dict(
            bw=self.bw, bh=self.bh, fw=self.fw, fh=self.fh, 
            fthresh=self.fthresh)
        return kws
        
    @property
    def sep_extract_kws(self):
        if self.kernel is not None:
            self.kernel.normalize()
            kern_arr = self.kernel.array
        else:
            kern_arr = None
        kws = dict(
           thresh=self.thresh, minarea=self.minarea, filter_kernel=kern_arr, 
           filter_type=self.filter_type, deblend_nthresh=self.deblend_nthresh, 
           deblend_cont=self.deblend_cont, clean=self.clean, 
           clean_param=self.clean_param, 
           segmentation_map=self.segmentation_map)
        return kws
