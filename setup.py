import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()


setup(
    name="gmalthgtparser",
    version=read('VERSION'),
    author="Jonathan Bouzekri",
    author_email="jonathan.bouzekri@gmail.com",
    description="Parse HGT files",
    license="MIT",
    keywords="parser, hgt, srtm, file",
    url="http://github.com/gmalt/hgtparser",
    packages=find_packages(exclude=["test"]),
    long_description=read('README.md'),
    extras_require={
        'test': ['pytest', 'flake8', 'mock']
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Utilities",
    ]
)
