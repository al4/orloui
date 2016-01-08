#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup
import multiprocessing  # nopep8

VERSION = '0.0.5-1'
version_file = open('./orloui/_version.py', 'w')
version_file.write("__version__ = '{}'".format(VERSION))
version_file.close()

setup(
    name='orloui',
    version=VERSION,
    description='User interface to Orlo',
    author='Alex Forbes',
    author_email='alforbes@ebay.com',
    license='GPL',
    long_description=open('README.md').read(),
    url='https://github.com/eBayClassifiedsGroup/orloui',
    packages=[
        'orloui',
    ],
    include_package_data=True,
    install_requires=[
        'Flask',
        'arrow',
        'gunicorn',
        'orloclient>=0.0.5',
        'pytz',
    ],
    tests_require=[
        'Flask-Testing',
    ],
    test_suite='tests',
)
