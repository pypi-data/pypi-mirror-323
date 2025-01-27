# setup.py

from setuptools import setup, find_packages

setup(
    name="harichselvamc",
    version="0.6",
    packages=find_packages(),
    description="A simple Python package to generate Pascal's Triangle.",
    long_description="""
    A Python package that generates Pascal's Triangle up to the specified number of rows. 
    The package is ideal for learning about number patterns and exploring the properties of binomial coefficients. 

    Features:
    - Generate the first N rows of Pascal's Triangle
    - Simple, easy-to-use interface
    
    This package may be extended in future versions to include optimizations and additional functionality.
    """,
    long_description_content_type="text/plain",
    author="harichselvam",
    author_email="harichselvamc@gmail.com",
    url="https://github.com/harichselvamc/harichselvamc",  # Replace with your GitHub URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=["pytest"],
    test_suite="tests",
)
