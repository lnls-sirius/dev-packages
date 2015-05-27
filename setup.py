#!/usr/bin/env python3

from setuptools import setup, find_packages

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
    platforms=['Linux', 'Mac Os X'],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['mathphys'],

    install_requires=[
        'numpy>=1.8.2',
        'lnls>=0.1.0'
    ],
    dependency_links=['https://github.com/lnls-fac/lnls/archive/v0.1.0.tar.gz#egg=lnls-0.1.0'],
)
