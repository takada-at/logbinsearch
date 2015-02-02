# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages, Extension

from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

setup(name='logbinsearch',
      version='0.0.1',
      description='',
      author='takada-at',
      author_email='takada-at@klab.com',
      packages=find_packages(),
      ext_modules=[
          Extension('logbinsearch.bz2search', 
                    ['src/bz2search.c', 'src/microbunzip.c']),
      ],
      tests_require=['pytest'],
      cmdclass = {'test': PyTest},
      scripts=['scripts/logdatetimesearch'],
)

