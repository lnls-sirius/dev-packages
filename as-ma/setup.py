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
    scripts=['scripts/sirius-ioc-tb-ma-dipole-fam.py',
             'scripts/sirius-ioc-tb-ma-corrector.py',
             'scripts/sirius-ioc-tb-ma-multipole.py',
             'scripts/sirius-ioc-bo-ma-dipole-fam.py',
             'scripts/sirius-ioc-bo-ma-corrector.py',
             'scripts/sirius-ioc-bo-ma-multipole-fam.py',
             'scripts/sirius-ioc-ts-ma-dipole-fam.py',
             'scripts/sirius-ioc-ts-ma-corrector.py',
             'scripts/sirius-ioc-ts-ma-multipole.py',
             'scripts/sirius-ioc-si-ma-dipole-fam.py',
             'scripts/sirius-ioc-si-ma-corrector-slow.py',
             'scripts/sirius-ioc-si-ma-corrector-fast.py',
             'scripts/sirius-ioc-si-ma-multipole-fam.py',
             'scripts/sirius-ioc-si-ma-quadrupole-trim.py',
             'scripts/sirius-ioc-as-pm.py'
             ],
    zip_safe=False
)
