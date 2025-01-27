from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='txtsearch',
  version='0.1',
  author='flovvi',
  author_email='flovvi78@gmail.com',
  description='This is a library for finding keywords in text files.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/FLOVVI/txtsearch',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='search txt files txtfiles txtsearch ',
  project_urls={
    'GitHub': 'https://github.com/FLOVVI'
  },
  python_requires='>=3.6'
)