#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup
import multiprocessing  # nopep8

VERSION = '0.0.4'
version_file = open('./orloWeb/_version.py', 'w')
version_file.write("__version__ = '{}'".format(VERSION))

setup(
    name='orloWeb',
    version=VERSION,
    description='User interface to Orlo',
    author='Alex Forbes',
    author_email='alforbes@ebay.com',
    license='GPL',
    long_description=open('README.md').read(),
    url='https://github.com/eBayClassifiedsGroup/orloWeb',
    packages=[
        'orloWeb',
    ],
    include_package_data=True,
    install_requires=[
        'Flask',
        'arrow',
        'gunicorn',
        'orloclient>=0.0.4',
        'pytz',
    ],
    tests_require=[
        'Flask-Testing',
    ],
    test_suite='tests',
)
