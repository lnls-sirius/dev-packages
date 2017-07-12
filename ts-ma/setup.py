#!/usr/bin/env python3

from setuptools import setup

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='ts-ma',
    version=__version__,
    author='lnls-sirius',
    description='TS Soft IOC for magnets',
    url='https://github.com/lnls-sirius/dev-packages',
    download_url='https://github.com/lnls-sirius/dev-packages',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['ts-ma'],
    package_data={'ts-ma': ['VERSION']},
    scripts=['ts-ma.py'],
    zip_safe=False
)
