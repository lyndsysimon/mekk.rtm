# -*- coding: utf-8 -*-
# (c) 2010, Marcin Kasperski

from setuptools import setup, find_packages
import os
execfile(os.path.join(os.path.dirname(__file__), "src", "mekk", "rtm", "version.py"))

long_description = open("README.txt").read()
classifiers = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # TODO: Development Status, Environment, Topic
    ]

setup(name='mekk.rtm',
      version=VERSION,
      description="RememberTheMilk client API and command line client",
      long_description=long_description,
      classifiers=classifiers,
      keywords='rtm,RememberTheMilk',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://bitbucket.org/Mekk/rtmimport',
      license='LGPL',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite = 'nose.collector',
      zip_safe=False,
      install_requires=[
        'simplejson', 
        'keyring>=0.3',
        'python-dateutil',
      ],
      tests_require=[
          'nose', 
          'Mock>=0.7b1',
      ],
      entry_points = {
        'console_scripts': [
            'rtmimport = mekk.rtm.helpers.run_import:run',
            'rtmtag = mekk.rtm.helpers.run_tag:run',
            'rtmmove = mekk.rtm.helpers.run_move:run',
            'rtmexport = mekk.rtm.helpers.run_export:run',
            ],
        },

)
