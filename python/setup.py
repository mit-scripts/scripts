#!/usr/bin/env python

from setuptools import setup

setup(
    name='sipb-jupyter',
    version='1.0',
    description='SIPB Jupyter Python Modles',
    author='SIPB Jupyter Team',
    author_email='sipb-jupyter@mit.edu',
    url='https://jupyter.mit.edu/',
    packages=['sipb.jupyter'],
    package_data={'sipb.jupyter': ['interface/*.varlink']},
)
