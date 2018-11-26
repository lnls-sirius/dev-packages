#!/usr/bin/env python-sirius
"""Siriuspy setup module."""

"""Siriuspy setup script."""


from setuptools import setup, find_packages

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

with open('requirements.txt', 'r') as _f:
    _requirements = _f.read().strip().split('\n')

setup(
    name='siriuspy',
    version=__version__,
    author='lnls-sirius',
    description='Development packages for Sirius',
    url='https://github.com/lnls-sirius/dev-packages',
    download_url='https://github.com/lnls-sirius/dev-packages',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=find_packages(),
    install_requires=_requirements,
    package_data={'siriuspy': ['VERSION']},
    data_files=[('siriuspy/mathphys/data',
                 ['siriuspy/mathphys/data/d_touschek.npz'])],
    test_suite='tests',
    zip_safe=False
)
