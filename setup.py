# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages, Extension
import os
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

shortdesc = "search (bz2)log file with binary search"

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fd:
    longdesc = fd.read()
with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fd:
    version = fd.read()
setup(name='logbinsearch',
      description=shortdesc,
      long_description=longdesc,
      version=version,
      author='takada-at',
      author_email='takada-at@klab.com',
      packages=find_packages(),
      ext_modules=[
          Extension('logbinsearch.bz2search', 
                    ['src/bz2search.c', 'src/microbunzip.c'], include_dirs=['src']),
      ],
      tests_require=['pytest'],
      cmdclass = {'test': PyTest},
      url = "https://github.com/takada-at/logbinsearch",
      scripts=['scripts/logdatetimesearch'],
)

