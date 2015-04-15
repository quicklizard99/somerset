#!/usr/bin/env python
from setuptools import setup

import somerset


setup(name='somerset',
      version=somerset.__version__,
      description=somerset.__doc__,
      author='Lawrence Hudson',
      author_email='l.hudson@nhm.ac.uk',
      scripts=['somerset.py'],
     )
