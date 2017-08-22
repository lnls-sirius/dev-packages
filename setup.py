#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='mathphys',
    version=__version__,
    author='lnls-fac',
    description='LNLS Math and Physics utilities',
    url='https://github.com/lnls-fac/mathphys',
    download_url='https://github.com/lnls-fac/mathphys',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['mathphys'],
    package_data={'mathphys': ['VERSION', 'data/d_touschek.npz']},
    zip_safe=False,
)
