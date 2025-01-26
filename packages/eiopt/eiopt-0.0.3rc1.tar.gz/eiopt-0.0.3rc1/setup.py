#!/usr/bin/env python
# -*-coding:utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

import os
from setuptools import setup, find_packages


with open('README.md', encoding="utf-8") as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='eiopt',
    version='0.0.3rc1',
    description='description for Sample package',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='zmdsn',
    author_email='zmdsn@126.com',
    url='http://www.eiopt.com/',
    install_requires=[
        'pymoo==0.6.1.3',
        'pyomo==6.8.2',
        'gurobipy==12.0.0'
        ],
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)