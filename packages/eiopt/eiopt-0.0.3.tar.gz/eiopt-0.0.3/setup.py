#!/usr/bin/env python
# -*-coding:utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

import os
from setuptools import setup, find_packages

def _process_requirements():
    packages = open('requirements.txt').read().strip().split('\n')
    requires = []
    for pkg in packages:
        if pkg.startswith('git+ssh'):
            return_code = os.system('pip install {}'.format(pkg))
            assert return_code == 0, 'error, status_code is: {}, exit!'.format(return_code)
        else:
            requires.append(pkg)
    return requires

with open('README.md', encoding="utf-8") as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='eiopt',
    version='0.0.3',
    description='description for Sample package',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='zmdsn',
    author_email='zmdsn@126.com',
    url='http://www.eiopt.com/',
    install_requires=_process_requirements(),
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
