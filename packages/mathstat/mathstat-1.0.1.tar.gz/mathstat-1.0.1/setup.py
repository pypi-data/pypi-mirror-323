from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='mathstat',
  version='1.0.1',
  author='amogusbazed',
  author_email='amogusbazed@gmail.com',
  description='Package mathstats contains mathematical and statistical functions, distributions, tests',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  classifiers=[
    'Programming Language :: Python :: 3.13',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files speedfiles ',
  python_requires='>=3.6'
)