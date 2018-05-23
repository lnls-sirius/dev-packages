#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-pu',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Power Supplies.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_pu'],
    package_data={'as_pu': ['VERSION']},
    scripts=['scripts/sirius-ioc-as-pu.py', ],
    zip_safe=False
)
