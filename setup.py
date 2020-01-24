from __future__ import unicode_literals

from io import open

from setuptools import setup

from minibelt import __version__

open("MANIFEST.in", "w").write("\n".join(("include *.rst",)))


setup(
    name="minibelt",
    version=__version__,
    author="Sam et Max",
    py_modules=["minibelt"],
    author_email="lesametlemax@gmail.com",
    description="One-file utility module filled with helper functions for day to day Python programming",
    long_description=open("README.rst", "r", encoding="utf-8").read(),
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: zlib/libpng License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
    ],
    url="https://github.com/sametmax/minibelt",
)
