# setup.py
from setuptools import setup, find_packages

setup(
    name='port_scanner',
    packages=find_packages('.', exclude=['tests', 'tests.*']),
)