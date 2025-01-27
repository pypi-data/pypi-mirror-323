from setuptools import setup


def readme():
  with open('README.md', 'r') as f:
    return f.read()

with open('requirements.txt') as f:
  r = [i.strip() for i in f.readlines() if i.strip()]

setup(
  name='core-api-tools',
  version='0.0.5',
  author='ZaharDimidov',
  author_email='zahar_dimidov@mail.ru',
  description='This is the simplest module for quick work with fastapi.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/zahardimidov/core-api-tools',
  packages=['core_api_tools'],
  install_requires=r,
  classifiers=[
    'Programming Language :: Python :: 3.12',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='fastapi',
  project_urls={
    'GitHub': 'https://github.com/zahardimidov/core-api-tools'
  },
  python_requires='>=3.10'
)


