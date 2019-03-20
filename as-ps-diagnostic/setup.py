#!/usr/bin/env python-sirius
"""Setup Module."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ps-diagnostic',
    version=__version__,
    author='lnls-sirius',
    description='Power Supply Current SP/Mon diagnostics',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ps_diagnostic'],
    package_data={'as_ps_diagnostic': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-as-ps-diagnostic.py',
             ],
    zip_safe=False
)
