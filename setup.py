#!/usr/bin/env python3

from distutils.core import setup

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='MathPhys',
    version=__version__, 
    description='LNLS Math and Physics utilities',
    url='https://github.com/lnls-fac/mathphys',
    packages=['mathphys'],
)
