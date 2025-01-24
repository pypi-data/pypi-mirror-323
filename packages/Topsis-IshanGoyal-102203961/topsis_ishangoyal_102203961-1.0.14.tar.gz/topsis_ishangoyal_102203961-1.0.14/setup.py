from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Topsis_IshanGoyal_102203961",
    version="1.0.14",
    author="Ishan Goyal",
    author_email="igoyal_be22@thapar.com",
    url="https://github.com/goyalishan/Topsis_102203961",
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
    entry_points={"console_scripts": ["Topsis_IshanGoyal_102203961 = Topsis_IshanGoyal_102203961.topsis:main"]},
)