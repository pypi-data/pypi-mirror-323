from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='numplot',
  version='0.0.9',
  author='amogusbazed',
  author_email='amogusbazed@gmail.com',
  description='Extension for math',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/EgorZhizhlo/TASK_CONTROL',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.13',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files speedfiles ',
  project_urls={
    'GitHub': 'https://github.com/EgorZhizhlo/TASK_CONTROL'
  },
  python_requires='>=3.6'
)