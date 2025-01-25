from setuptools import setup, find_packages
from pathlib import Path
import codecs
import os

VERSION = '1.0.22'
DESCRIPTION = 'Topsis technique for MCDM'
from pathlib import Path
this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="topsis_mohit_102397005",
    version=VERSION,
    author="Mohit Bansal",
    author_email="mohitbansal0031@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pandas', 'numpy'],
    keywords=['python', 'topsis', 'mcdm', 'decision making'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)