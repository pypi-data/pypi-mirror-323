from setuptools import setup

setup(
    name="102217186_abhaijeet_topsis",
    version="1.0.0",
    author="Abhaijeet Singh",
    author_email="asingh37_be22@thapar.edu",
    description="A Python package for TOPSIS calculation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AbhaijeetSingh11/102217186_abhaijeet_topsis",
    packages=["102217186_abhaijeet_topsis"],
    install_requires=[
        "numpy",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "102217186_abhaijeet_topsis=102217186_abhaijeet_topsis.topsis:main",
        ],
    },
)
