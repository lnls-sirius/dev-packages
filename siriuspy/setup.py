#!/usr/bin/env python-sirius

"""Siriuspy setup script."""

import pkg_resources
from setuptools import find_packages, setup


def get_abs_path(relative):
    return pkg_resources.resource_filename(__name__, relative)


with open(get_abs_path("README.md"), "r") as _f:
    _long_description = _f.read().strip()

with open(get_abs_path("VERSION"), "r") as _f:
    __version__ = _f.read().strip()

with open(get_abs_path("requirements.txt"), "r") as _f:
    _requirements = _f.read().strip().split("\n")

setup(
    name="siriuspy",
    version=__version__,
    author="lnls-sirius",
    description="Development packages for Sirius",
    long_description=_long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lnls-sirius/dev-packages",
    download_url="https://github.com/lnls-sirius/dev-packages",
    license="GNU GPLv3",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
    ],
    packages=find_packages(),
    install_requires=_requirements,
    package_data={"siriuspy": ["VERSION"]},
    include_package_data=True,
    test_suite="tests",
    python_requires=">=3.6",
    zip_safe=False,
)
