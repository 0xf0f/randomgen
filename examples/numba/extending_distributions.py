r"""
On *nix, execute in core_prng/src/distributions

export PYTHON_INCLUDE=#path to Python's include folder, usually ${PYTHON_HOME}/include/python${PYTHON_VERSION}m
export NUMPY_INCLUDE=#path to numpy's include folder, usually ${PYTHON_HOME}/lib/python${PYTHON_VERSION}/site-packages/numpy/core/include
gcc -shared -o libdistributions.so -fPIC distributions.c -I${NUMPY_INCLUDE} -I${PYTHON_INCLUDE}
mv libdistributions.so ../../../examples/numba/

On Windows

rem PYTHON_HOME is setup dependent, this is an example
set PYTHON_HOME=c:\Anaconda
cl.exe /LD .\distributions.c -DDLL_EXPORT -I%PYTHON_HOME%\lib\site-packages\numpy\core\include -I%PYTHON_HOME%\include %PYTHON_HOME%\libs\python36.lib
move distributions.dll ../../../examples/numba/
"""
import os
import numpy as np
from cffi import FFI
from core_prng import Xoroshiro128
import numba as nb

ffi = FFI()
if os.path.exists('./distributions.dll'):
    lib = ffi.dlopen('./distributions.dll')
elif os.path.exists('./libdistributions.so'):
    lib = ffi.dlopen('./libdistributions.so')
else:
    raise RuntimeError('Required DLL/so file was not found.')

ffi.cdef("""
double random_gauss(void *prng_state);
double random_gauss_zig(void *prng_state);
""")
x = Xoroshiro128()
xffi = x.cffi
prng = xffi.prng

random_gauss = lib.random_gauss
random_gauss_zig = lib.random_gauss_zig


def normals(n, prng):
    out = np.empty(n)
    for i in range(n):
        out[i] = random_gauss(prng)
    return out


def normals_zig(n, prng):
    out = np.empty(n)
    for i in range(n):
        out[i] = random_gauss_zig(prng)
    return out


normalsj = nb.jit(normals, nopython=True)
normals_zigj = nb.jit(normals_zig, nopython=True)

# Numba requires a memory address for void *
# Can also get address from x.ctypes.prng.value
prng_address = int(ffi.cast('uintptr_t', prng))

norm = normalsj(1000, prng_address)
norm_zig = normals_zigj(1000, prng_address)