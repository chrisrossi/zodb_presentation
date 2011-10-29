from setuptools import setup
from setuptools import find_packages

VERSION = '0.0'

requires = [
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
      """)
