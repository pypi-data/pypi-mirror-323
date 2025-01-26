# setup.py
from setuptools import setup, find_packages

VERSION = "0.1.0"
DESCRIPTION ="Python NinjaTrader Client Library"
# LONG_DESCRIPTION =open("README.md", 'r').read(),,
LONG_DESCRIPTION =""

setup(
    name="ntclient",
    version=VERSION,
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.11",
    author="Amer Jod",
    author_email="amer.j.eng@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/OrcaVenturers/ntclient",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)