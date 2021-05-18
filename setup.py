"""Builds the library.

To upload to cheese:

sudo pip3 install twine
sudo python3 setup.py sdist bdist_wheel
twine upload  --skip-existing dist/* --verbose
"""

from setuptools import find_packages, setup

setup(
    name="dolon",
    description="A performance tracer application.",
    version='0.0.16',
    packages=find_packages(),
    install_requires=[
        "asyncpg"
    ],
)
