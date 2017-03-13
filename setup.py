#! /usr/bin/env python

# Standard library
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="ashd",
    version='v0.1',
    author="Johnny Greco",
    author_email="jgreco@astro.princeton.edu",
    packages=["ashd"],
    url="https://github.com/johnnygreco/asas-sn-hd",
    license="MIT",
    description="Hunt for dwarf galaxies with ASAS-SN",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
