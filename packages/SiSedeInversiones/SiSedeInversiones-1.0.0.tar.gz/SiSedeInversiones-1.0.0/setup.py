import pathlib

import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
with open(HERE / "README.md", encoding="utf-8") as f:
    README = f.read()

setuptools.setup(
    name="SiSedeInversiones",
    version="1.0.0",
    author="Jelsin Stalin Palomino Huaytapuma",
    author_email="jstpalomino@hotmail.com",
    description="This package is dedicated to automating the extraction of data found in the Peruvian state's Investment Monitoring System - SSI portal, where public investment projects in Peru can be monitored through Unique Investment Codes (CUI).",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/JelsinPalomino/SiSedeInversiones",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Intended Audience :: Education",
    ],
    install_requires=["pandas", "rpa", "openpyxl"],
    keywords=["web-scraping", "Peru", "rpa", "SSI", "Inversiones"],
)
