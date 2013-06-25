#!/usr/bin/env python

from distutils.core import setup

# import py2app
# setup( app=['SalimApp.py'] )

setup(name="salim",
      version="0.1.0",
      package_dir={'salim': 'salim'},
      packages=['salim'],
      author='Wilson Freitas',
      author_email='wilson.freitas@gmail.com',
      description='An API to build a personal finance system',
      url='http://aboutwilson.net/salim',
      license='GPL',
      long_description='''\
''',
      scripts = ["scripts/salim"],
      )
