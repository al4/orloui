#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup
import multiprocessing  # nopep8

setup(
    name='orloWeb',
    version='0.0.1',
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
        'pytz',
    ],
    tests_require=[
        'Flask-Testing',
    ],
    test_suite='tests',
)
