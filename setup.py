from setuptools import setup

setup(name='CorpusInterface',
      version='0.1',
      description='tools for loading musical corpora',
      url='https://github.com/DCMLab/CorpusInterface.git',
      author='Robert Lieck',
      # author_email='',
      # license='',
      packages=['CorpusInterface'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'])
