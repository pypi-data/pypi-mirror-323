from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='interp-tools',
  version='1.0.12',
  author='Mof1us',
  author_email='antoon.s.ivanov@gmail.com',
  description='Interpolation Tool for 1d 2d and 3d functions',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://google.com',
  packages=find_packages(),
  install_requires=['numpy'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='interpolation, 1d interpolation, 2d interpolation, 3d interpolation, functions, tools',
  project_urls={
  },
  python_requires='>=3.7'
)