#!/usr/bin/env python-sirius
"""Siriuspy setup module."""

from setuptools import setup, find_packages

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='siriuspy',
    version=__version__,
    author='lnls-sirius',
    description='Sirius python packages',
    url='https://github.com/lnls-sirius/dev-packages',
    download_url='https://github.com/lnls-sirius/dev-packages',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=find_packages(),
    package_data={'siriuspy': ['VERSION']},
    data_files=[('siriuspy/mathphys/data',
                 ['siriuspy/mathphys/data/d_touschek.npz'])],
    test_suite='tests',
    zip_safe=False
)
