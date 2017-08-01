#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ma',
    version=__version__,
    author='lnls-sirius',
    description='AS Soft IOC for magnets',
    url='https://github.com/lnls-sirius/dev-packages',
    download_url='https://github.com/lnls-sirius/dev-packages',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as-ma'],
    package_data={'as-ma': ['VERSION']},
    scripts=['as-ma.py'],
    zip_safe=False
)
