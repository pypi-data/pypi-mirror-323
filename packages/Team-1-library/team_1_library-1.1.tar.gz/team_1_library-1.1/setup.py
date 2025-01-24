from setuptools import setup, find_packages

setup(
name="Team_1_library",
version="1.1",
description="Data prerpocess library with missing value imputation and outlier correction functions.",
long_description=open("README.md").read(),
long_description_content_type="text/markdown",
author="Jokin Agirre, Irene Alvarez, Uxue Auzmendi, Jon Lorenzo, Manex Ugarte ",
author_email="manex.ugarte@alumni.mondragon.edu",
url="https://github.com/Manex14/Team_1_library",
packages=find_packages(),
include_package_data=True,
install_requires=[
        "pandas",
        "scipy",
        "numpy",
        "scikit-learn",
        "fuzzywuzzy"
    ],
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
],
python_requires=">=3.8",
)