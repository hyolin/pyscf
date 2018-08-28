"""Setup for python."""
from setuptools import setup, find_packages

__version__ = '0.0.1'

setup(
    name='pyscf',
    version=__version__,
    author='hyolin',
    author_email='hyolin.han#gmail.com',
    description='',
    packages=find_packages(),
    include_package_data=True,
)
