#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='siriusdm',
    version=__version__,
    author='lnls-sirius',
    description='Sirius Display Manager',
    url='https://github.com/lnls-sirius/dev-packages',
    download_url='https://github.com/lnls-sirius/dev-packages',
    license='Custom License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=find_packages(),
    package_data={'siriusdm': ['VERSION']},
    zip_safe=False
)
