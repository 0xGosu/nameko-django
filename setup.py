#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  setup.py
#  
#
#  Created by vincenttran on 2019-09-02.
#  Copyright (c) 2019 bentodatabase. All rights reserved.
#
import os, sys

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'rb') as f:
    long_description = f.read().decode('utf8')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nameko_django/VERSION')) as f:
    __version__ = f.read()

from setuptools import setup

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner==5.1'] if needs_pytest else []

setup(
    name='nameko-django',
    version=__version__,
    description='Django intergration for nameko microservice framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tranvietanh1991/nameko-django',
    author='Vincent Anh Tran',
    author_email='tranvietanh1991@gmail.com',
    maintainer='Vincent Anh Tran',
    maintainer_email='vincent.tran@bentoinvest.cloud',
    license='GPLv2',
    packages=['nameko_django'],
    zip_safe=False,
    install_requires=[
        'nameko>=2.11.0',
        'django>=1.10',
        'msgpack>=1.0.0',
        'aenum>=2.1.0'
    ],
    setup_requires=[
                   ] + pytest_runner,
    test_suite='nose.collector',
    tests_require=['pyparsing==2.4.2', 'nose==1.3.7', 'pytest==4.6.6', 'pytest-django==3.6.0', 'python-box==3.2.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'kombu.serializers': [
            'django_msgpackpickle = nameko_django.serializer:register_args'
        ]
    }
)
