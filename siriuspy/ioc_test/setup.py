#!/usr/bin/env python3

"""IOC test package setup script."""


from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='PROJECT-NAME',
    version=__version__,
    author='lnls-sirius',
    description='PROJECT-DESCRIPTION',
    url='PROJECT-URL',
    download_url='PROJECT-DOWNLOAD-URL',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['PROJECT-NAME'],
    package_data={'PROJECT-NAME': ['VERSION']},
    scripts=[],
    zip_safe=False
)
