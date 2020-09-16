"""new_pytest_needle

.. codeauthor:: P.Serega

"""

from setuptools import setup
import os
from setuptools import setup
from new_pytest_needle import __author__, __email__, __license__, __version__


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(name='new_pytest_needle',
      version=__version__,
      author=__author__,
      author_email=__email__,
      description='VT pytest + selenium',
      license=__license__,
      keywords='pytest needle imagemagick Pillow selenium VT',
      url=u'https://github.com/Gadzillion/new_pytest_needle',
      packages=['new_pytest_needle'],
      entry_points={'pytest11': ['needle = new_pytest_needle.plugin', ]},
      long_description=read("../README.md"),
      long_description_content_type="text/markdown",
      install_requires=[
          'pytest',
          'pytest-selenium',
          'needle',
          'selenium',
          'allure'
      ],
      python_requires=">=3.6",
      classifiers=[
          'Development Status :: 1 - Planning',
          'Framework :: Pytest',
          'Intended Audience :: Science/Research',
          "Natural Language :: English",
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          'Topic :: Utilities'
      ])
