from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = 'Extension / Wrapper for structlog library.'
LONG_DESCRIPTION = (Path(__file__).parent / 'README.md').read_text()

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="elastic_structlog",
    version="0.2.5",
    author="Nuriel Gadilov",
    author_email="nurielprivet@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["elasticsearch==8.17.0", "structlog==24.4.0"],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'structlog', 'es', "elastic"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
