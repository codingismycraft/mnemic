"""Builds the library.

To upload to cheese:

sudo pip3 install twine
rm -rf build dist
sudo python3 setup.py sdist bdist_wheel
twine upload  --skip-existing dist/* --verbose
"""
import pathlib

from setuptools import find_packages, setup

_ROOT = pathlib.Path(__file__).parent

with open(str(_ROOT / 'README.rst')) as f:
    readme = f.read()

setup(
    name="dolon",
    description="A performance tracer application.",
    long_description=readme,
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        "asyncpg",
        "aiohttp",
        "psutil"
    ],
)
