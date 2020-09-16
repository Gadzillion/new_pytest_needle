"""new_pytest_needle

.. codeauthor:: P.Serega

"""

from setuptools import setup
import os
from setuptools import setup
from pytest_needle import __author__, __email__, __license__, __version__


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
      long_description=read("README.md"),
      long_description_content_type="text/markdown",
      install_requires=[
          'pytest>=3.7.0,<5.0.0',
          'pytest-selenium>=1.16.0,<2.0.0',
          'needle>=0.5.0,<0.6.0',
          'selenium>=3.0.0'
      ],
      python_requires=">=2.7",
      tests_require=[
          "pytest-cov>=2.7.0",
          "python-coveralls>=2.9.0",
          "pytest-pep8>=1.0.0"
      ],
      extras_require={
          "release": [
              "bumpversion>=0.5.0",
              "recommonmark>=0.5.0",
              "Sphinx>=1.8.0",
              "sphinx-autobuild>=0.7.0",
              "sphinx-rtd-theme>=0.4.0",
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Pytest',
          'Intended Audience :: Developers',
          "Natural Language :: English",
          'Operating System :: POSIX',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          'Topic :: Utilities'
      ])

setup(
    name='new_pytest_needle',
    version='0.0.1',
    description='VT Python package',
    url='https://github.com/Gadzillion/pytest-needle',
    author='Sergey P',
    author_email='serjojo1@gmail.com',
    license='BSD 2-clause',
    packages=['pyexample'],
    install_requires=['mpi4py>=2.0',
                      'numpy',
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)