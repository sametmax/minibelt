
from setuptools import setup, find_packages

open('MANIFEST.in', 'w').write('\n'.join((
    "include *.rst",
)))

from minibelt import __version__

setup(

    name="minibelt",
    version=__version__,
    packages=find_packages('.'),
    author="Sam et Max",
    author_email="lesametlemax@gmail.com",
    description="One-file utility module filled with helper functions for day to day Python programming",
    long_description=open('README.rst').read(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: zlib/libpng License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.3"
    ],
    url="https://github.com/sametmax/minibelt"
)

