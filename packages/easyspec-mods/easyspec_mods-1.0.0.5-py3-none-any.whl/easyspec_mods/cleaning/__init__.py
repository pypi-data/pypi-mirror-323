__version__ = '1.0.0'

import numpy as np
# from mpl_toolkits.axes_grid1 import make_axes_locatable #this is to adjust the colorbars
# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
# import glob
# from astropy.io import fits
# from scipy import stats as st
# from pathlib import Path
# import warnings
# from scipy import odr
# from astropy.nddata import CCDData
# from astropy import units as u
# import ccdproc as ccdp
import os
# from scipy.signal import medfilt

from .cleaning import *

bias_list = []
flat_list = []
lamp_list = []
std_list = []
target_list = []
darks_list = []

