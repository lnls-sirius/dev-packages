#!/usr/bin/env python3

from setuptools import setup

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-fam-ma',
    version=__version__,
    author='lnls-sirius',
    description='Soft IOC for magnets',
    url='https://github.com/lnls-sirius/dev-packages',
    download_url='https://github.com/lnls-sirius/dev-packages',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si-fam-ma'],
    package_data={'si-fam-ma': ['VERSION']},
    scripts=['si-fam-ma.py'],
    zip_safe=False
)
