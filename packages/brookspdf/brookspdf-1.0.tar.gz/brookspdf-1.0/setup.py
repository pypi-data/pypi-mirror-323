import setuptools
from pathlib import Path

setuptools.setup(
    name="brookspdf",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["test", "data"])

)
# 5:50 in PUBLISHING PACKAGES
