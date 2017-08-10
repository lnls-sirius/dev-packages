#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ps-test',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Simulating Power Supplies.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ps_test'],
    package_data={'as_ps_test': ['VERSION']},
    scripts=['scripts/sirius-ioc-as-ps-test.py', ],
    zip_safe=False
)
