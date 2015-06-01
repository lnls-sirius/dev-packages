#!/usr/bin/env python3

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
    package_data={'mathphys': ['VERSION']},

    # install_requires=[
    #     'numpy>=1.8.2',
    #     'lnls>=0.1.0'
    # ],
    # dependency_links=['https://github.com/lnls-fac/lnls/archive/v0.1.0.tar.gz#egg=lnls-0.1.0'],
    zip_safe=False,
)
