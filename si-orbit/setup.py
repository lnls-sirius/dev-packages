#!/usr/bin/env python3
"""Setup Module."""
from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='IOCOrbit',
    version=__version__,
    author='lnls-sirius',
    description='Orbit IOC for Sirius',
    url='PROJECT-URL',
    download_url='PROJECT-DOWNLOAD-URL',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['Orbit'],
    package_data={'Orbit': ['VERSION']},
    scripts=[],
    zip_safe=False
)
