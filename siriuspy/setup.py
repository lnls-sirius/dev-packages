#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='psirius',
    version=__version__,
    author='lnls-sirius',
    description='Sirius python packages',
    url='https://github.com/lnls-sirius/python-packages',
    download_url='https://github.com/lnls-sirius/python-packages',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=find_packages(),
    package_data={'psirius': ['VERSION']},
    zip_safe=False
)
