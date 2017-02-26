#!/usr/bin/env python3

from setuptools import setup, find_packages

import git
repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha

with open('VERSION','w') as _f:
    __version__ = _f.write(str(sha))

setup(
    name='psirius',
    version=__version__,
    author='lnls-sirius',
    description='Sirius python packages',
    url='https://github.com/lnls-sirius/python-packages',
    download_url='https://github.com/lnls-sirius/python-packages',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=find_packages(),
    package_data={'psirius': ['VERSION']},
    zip_safe=False
)
