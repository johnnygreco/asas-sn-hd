#! /usr/bin/env python

# Standard library
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="asshugs",
    version='v0.1',
    author="Johnny Greco",
    author_email="jgreco@astro.princeton.edu",
    packages=["asshugs"],
    url="https://github.com/johnnygreco/asas-sn-hugs",
    license="MIT",
    description="Search for diffuse galaxies with ASAS-SN",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
