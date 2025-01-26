"""`odrpack` is a package for weighted orthogonal distance regression (ODR), also
known as errors-in-variables regression. It is designed primarily for instances
when both the explanatory and response variables have significant errors.
The package implements a highly efficient algorithm for minimizing the sum of
the squares of the weighted orthogonal distances between each data point and the
curve described by the model equation, subject to parameter bounds. The nonlinear
model can be either explicit or implicit. Additionally, `odrpack` can be used to
solve the ordinary least squares problem where all of the errors are attributed
to the observations of the dependent variable.
"""


# start delvewheel patch
def _delvewheel_patch_1_10_0():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'odrpack.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

__version__ = '0.2.0'

from odrpack.driver import *
from odrpack.exceptions import *
from odrpack.result import *