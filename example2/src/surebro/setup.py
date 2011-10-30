from setuptools import setup
from setuptools import find_packages

VERSION = '0.0'

requires = [
    'docutils',
    'pyramid',
    'pyramid_tm',
    'pyramid_zodbconn',
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
      [paste.app_factory]
      main = surebro.application:make_app
      """)
