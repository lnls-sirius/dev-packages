#!/usr/bin/env python3
"""Setup Module."""
from setuptools import setup

with open('VERSION', 'r') as _f:
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
    packages=['si_ap_orbit', 'si_ap_sofb'],
    package_data={'si_ap_orbit': [], 'si_ap_sofb': []},
    scripts=['scripts/sirius-ioc-si-ap-orbit',
             'scripts/sirius-ioc-si-ap-sofb'],
    zip_safe=False
)
