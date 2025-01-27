# setup.py

from setuptools import setup, find_packages

setup(
    name="harichselvamc",
    version="0.1",
    packages=find_packages(),
    description="A simple Python package for generating Pascal's Triangle.",
    author="harichselvam",
    author_email="harichselvamc@gmail.com",
    url="https://github.com/harichselvamc",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=["pytest"],
    test_suite="tests", 
) 
