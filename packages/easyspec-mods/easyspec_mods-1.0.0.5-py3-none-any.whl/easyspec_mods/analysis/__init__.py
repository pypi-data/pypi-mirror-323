__version__ = '1.0.0'

# import numpy as np
# import scipy
# from astropy.modeling.models import Gaussian1D, Voigt1D, Lorentz1D
# import matplotlib.pyplot as plt
# import emcee
# import corner
# import glob
from pathlib import Path
# from multiprocessing import Pool
# import time
# import warnings
# from matplotlib.ticker import AutoMinorLocator
# from scipy import interpolate
# from astropy import units as u
# from scipy.signal import medfilt
import platform
# import os
# from scipy.integrate import quad
# from astropy.constants import c
# from astropy.cosmology import FlatLambdaCDM
from .analysis import *
from ..extraction import extraction

# plt.rcParams.update({'font.size': 12})
OS_name = platform.system()
libpath = Path(__file__).parent.resolve() / Path("lines")

line_names = []
output_dir = ""
