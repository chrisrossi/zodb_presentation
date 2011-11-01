from setuptools import setup
from setuptools import find_packages

VERSION = '0.0'

requires = [
    'docutils',
    'jove',
    'jove_catalog',
    'pyramid',
    'pyramid_tm',
    'pyramid_zodbconn',
    'repoze.catalog',
    'repoze.folder',
    'ZODB3',
]

setup(name='surebro',
      version=VERSION,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      test_suite="nose.collector",
      entry_points="""\
      [jove.application]
      main = surebro.application:Main
      """)
