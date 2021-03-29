import re
from setuptools import setup

with open('README.md') as readme:
    long_description = readme.read()


def get_version(filename='addcopyfighandler.py'):
    """ Extract version information stored as a tuple in source code """
    version = ''
    with open(filename, 'r') as fp:
        for line in fp:
            m = re.search("__version__ = '(.*)'", line)
            if m is not None:
                version = m.group(1)
                break
    return version


# What packages are required for this module to be executed?
REQUIRED = [
    'matplotlib',
    'pywin32;platform_system=="Windows"',
]

setup(
    name="addcopyfighandler",
    version=get_version(),

    py_modules=["addcopyfighandler"],

    install_requires=REQUIRED,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    # metadata for upload to PyPI
    author="Josh Burnett",
    author_email="github@burnettsonline.org",
    description="Adds a Ctrl+C handler to matplotlib figures for copying the figure to the clipboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="addcopyfighandler figure matplotlib handler copy",
    url="https://github.com/joshburnett/addcopyfighandler",
    platforms=['windows', 'linux'],
)
