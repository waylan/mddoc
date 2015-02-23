#!/usr/bin/env python

from setuptools import setup
from mddoc import __version__ as ver

setup(
    name='mddoc',
    description='Markdown API Documenter',
    author='Waylan Limberg',
    author_email='waylan.limberg@icloud.com',
    version=ver,
    url='https://github.com/waylan/mddoc',
    packages=['mddoc'],
    install_requires = ['markdown>=2.6'],
    license='BSD'
)