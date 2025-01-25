from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="CoreEase",
    version="0.2.8",
    author="Casbian",
    description="A Python package to standardize my workflows and simplify repetitive tasks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Casbian/CoreEase",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
