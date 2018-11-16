#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ma',
    version=__version__,
    author='lnls-sirius',
    description='IOC for High Level control of Magnet Power Supplies.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ma'],
    package_data={'as_ma': ['VERSION']},
    scripts=['scripts/sirius-ioc-as-pm.py',
             'scripts/sirius-ioc-as-ma.py',
             ],
    zip_safe=False
)
