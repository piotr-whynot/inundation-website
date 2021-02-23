from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules = cythonize("model_delta_cython.pyx"),
    #ext_modules = cythonize("model_boteti_cython.pyx"),
    include_dirs=[numpy.get_include()]
)
