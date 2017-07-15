#!/usr/bin/env python3

from setuptools import setup

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='SOFB',
    version=__version__,
    author='lnls-sirius',
    description='Slow Orbit Feedback System for Sirius',
    url='PROJECT-URL',
    download_url='PROJECT-DOWNLOAD-URL',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['SOFB'],
    package_data={'SOFB': ['VERSION']},
    scripts=[],
    zip_safe=False
)
