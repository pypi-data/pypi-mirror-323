__version__ = '1.0.0'

# from astropy.io import fits
# import numpy as np
# import scipy
# from astropy.modeling.models import Gaussian1D
# import matplotlib.pyplot as plt
# import glob
from pathlib import Path
# from scipy import interpolate
# from astropy.modeling.polynomial import Polynomial1D
# from astropy.modeling.fitting import LinearLSQFitter, LevMarLSQFitter
# from astropy import units as u
# from scipy.signal import medfilt
# from dust_extinction.parameter_averages import F99
# import warnings
from .extraction import *
from ..cleaning import cleaning


# plt.rcParams.update({'font.size': 12})
libpath = Path(__file__).parent.resolve() / Path("airmass")
libpath_std = Path(__file__).parent.resolve() / Path("standards")

image_shape = []
aspect_ratio = 0
airmass_target = ""
airmass_std_star = ""
