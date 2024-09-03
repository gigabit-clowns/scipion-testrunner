"""
A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path
from dummy import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="scipion-em-dummy",  # Required
    version=__version__,  # Required
    description="Dummy Scipion plugin in order to perform E2E testing",  # Required
    long_description=long_description,  # Optional
    url="https://github.com/gigabit-clowns/scipion-testrunner/tests/e2e/scipion-em-dummy",  # Optional
    author="Martín Salinas",  # Optional
    author_email="ssalinasmartin@gmail.com",  # Optional
    keywords="scipion E2E",  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        #   'Intended Audience :: Users',
        # Pick your license as you wish
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=[requirements],
    entry_points={"pyworkflow.plugin": "dummy = dummy"},
    package_data={  # Optional
        "dummy": ["protocols.conf"],
    },
    project_urls={  # Optional
        "Bug Reports": "https://github.com/gigabit-clowns/scipion-testrunner/issues",
        "Pull Requests": "https://github.com/gigabit-clowns/scipion-testrunner/pulls",
    },
)
