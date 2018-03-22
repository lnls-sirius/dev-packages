#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ti-ll-simul',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Low Level Simulation of Sirius Timing System.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ti_ll_simul'],
    package_data={'as_ti_ll_simul': ['VERSION']},
    scripts=['scripts/sirius-ioc-as-ti-ll-simul.py'],
    zip_safe=False
)
