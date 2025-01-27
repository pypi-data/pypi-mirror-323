from setuptools import setup, find_packages # type: ignore

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Topsis_AbhiroopSingh_102213027",
    version="1.0.14",
    author="Abhiroop Singh",
    author_email="asingh34_be22@thapar.edu",
    url="https://github.com/ASingh917/Topsis_102213027",
    description="A python package for implementing topsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas", "numpy"],
    entry_points={"console_scripts": ["Topsis_AbhiroopSingh_102213027 = Topsis_AbhiroopSingh_102213027.topsis:main"]},
)