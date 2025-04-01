# -*- coding: UTF-8 -*-

import setuptools
from setuptools import setup, find_packages

# read the contents of your README file
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nokia-olt-device-harvester",
    version="0.0.2",
    author="David Johnnes",
    author_email="david.johnnes@gmail.com",
    description="""Network Automation and Programmability Abstraction for Nokia OLT.
    This package is intended to be used by applications that
    need to feed the network 'Single Source Of Truth' with the
    exact physical state of the network topology with 100% accuracy."""
    ,
    keywords="nokia, olt, devices harvester",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
    url="https://github.com/djohnnes/",
    include_package_data=True,
    install_requires=('mac-vendor-lookup', 'paramiko', 'sshFRIEND'),
)   
