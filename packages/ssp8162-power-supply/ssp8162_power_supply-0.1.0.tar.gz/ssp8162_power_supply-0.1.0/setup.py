# setup.py
from setuptools import setup, find_packages

setup(
    name="ssp8162_power_supply",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pyserial',  # Make sure pyserial is installed as a dependency
    ],
    description="A Python package to control the SSP-8162 power supply via serial communication.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Julian Steffens and Robin Binger",
    author_email="juliansf@mail.uni-paderborn.de",
    url="https://github.com/juliansteffens/ssp8162_power_supply",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
