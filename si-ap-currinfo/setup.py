#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-ap-currinfo',
    version=__version__,
    author='lnls-sirius',
    description='Soft IOC for SI Electron Beam Current Informations.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_ap_currinfo'],
    package_data={'si_ap_currinfo': ['VERSION']},
    scripts=['scripts/sirius-ioc-si-ap-currinfo-lifetime.py',
             'scripts/sirius-ioc-si-ap-currinfo-charge.py',
             'scripts/sirius-ioc-si-ap-currinfo-current.py'],
    zip_safe=False
)
