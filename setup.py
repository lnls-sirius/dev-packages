#!/usr/bin/env python3

#from distutils.core import setup
from setuptools import setup, find_packages


setup(
    name='mathphys',
    version='0.1.0',
    description='LNLS Math and Physics utilities',
    url='https://github.com/lnls-fac/mathphys',
    package_dir={'mathphys': 'src'},
    packages=find_packages(),

    install_requires=['lnls==0.1'],
    dependency_links=['https://github.com/lnls-fac/lnls/archive/v0.1.0.tar.gz#egg=lnls-0.1.0'],
)
