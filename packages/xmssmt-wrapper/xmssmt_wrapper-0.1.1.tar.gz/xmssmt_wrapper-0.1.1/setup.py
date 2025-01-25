from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# List of C source files
c_sources = [
    os.path.join('xmss-reference', 'xmss_core.c'),
    os.path.join('xmss-reference', 'hash.c'),
    os.path.join('xmss-reference', 'utils.c'),  # Add this line
    os.path.join('xmss-reference', 'xmss_commons.c'),
    os.path.join('xmss-reference', 'wots.c'),
    os.path.join('xmss-reference', 'randombytes.c'),
    os.path.join('xmss-reference', 'fips202.c'),
    os.path.join('xmss-reference', 'hash_address.c'),
    os.path.join('xmss-reference', 'params.c'),
    #os.path.join('xmss-reference', 'xmss_core_fast.c'),

    # Add other C source files as needed
]

# Include directories
include_dirs = [
    'xmss-reference',
    '/usr/include/openssl',
    # Add other include directories if needed
]

# Library directories
library_dirs = [
    #'/usr/lib',  # Adjust based on your system
    '/usr/lib/x86_64-linux-gnu',  # For Ubuntu/Debian
    # On macOS with Homebrew:
    # '/usr/local/opt/openssl/lib/',
]

# Libraries to link against
libraries = [
    'ssl',
    'crypto',
]
# Define the extension module
extensions = [
    Extension(
        name='xmssmt_wrapper',
        sources=['xmssmt_wrapper.pyx'] + c_sources,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        language='c',
    )
]

# Setup script
setup(
    name='xmssmt_wrapper',
    version='0.1.1', 
    description='Python wrapper of XMSSMT',
    author='Jim HE',
    author_email='jimheapps@gmail.com',
    license='MIT',
    ext_modules=cythonize(extensions),
    setup_requires=["cython"],
)