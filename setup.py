#!/usr/bin/env python-sirius

import versioneer
from setuptools import setup


setup(
    name='mathphys',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='lnls-fac',
    description='LNLS Math and Physics utilities',
    url='https://github.com/lnls-fac/mathphys',
    download_url='https://github.com/lnls-fac/mathphys',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['mathphys'],
    package_data={'mathphys': ['VERSION', 'data/d_touschek.npz']},
    zip_safe=False,
)
