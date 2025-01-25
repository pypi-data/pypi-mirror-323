# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='landowner',
    version='0.1.0',
    packages=find_packages(exclude=('tests', 'docs')),
    description='A Python package for working with export files of your personal data from the big social media platforms.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Drop Table Records',
    author_email='info@droptablerecords.com',
    url='https://github.com/droptablerecords/landowner',
    license=license,
)
