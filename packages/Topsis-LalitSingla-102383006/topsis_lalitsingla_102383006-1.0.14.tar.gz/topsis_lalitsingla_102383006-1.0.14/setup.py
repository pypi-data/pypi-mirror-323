from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Topsis_LalitSingla_102383006",
    version="1.0.14",
    author="Lalit Singla",
    author_email="lsingla_be22@thapar.edu",
    url="https://github.com/lalit-singla/Topsis_102383006",
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
    entry_points={"console_scripts": ["Topsis_LalitSingla_102383006 = Topsis_LalitSingla_102383006.topsis:main"]},
)