from setuptools import setup, find_packages

setup(
    name="Topsis_AgambirSinghDuggal_102203130",
    version="1.0.14",
    author="Agambir Singh Duggal",
    author_email="aduggal_be22@thapar.edu",
    description="A Python package for implementing the TOPSIS method.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/agamduggal/Predictive_Analysis_Topsis_102203130", 
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
