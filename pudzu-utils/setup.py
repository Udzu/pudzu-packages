from setuptools import setup, find_namespace_packages

VERSION='0.9.1'
URL='https://github.com/Udzu/pudzu-packages/'
AUTHOR='Uri Granta'
AUTHOR_EMAIL='uri.granta+python@gmail.com'
LICENSE='MIT'
CLASSIFIERS=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
]
PYTHON_REQUIRES='~=3.6'

setup(name='pudzu-utils', version=VERSION, packages=find_namespace_packages(include=['pudzu.*']),
      description='Various utility functions and data structures used by the other pudzu packages.',
      keywords='pudzu utilities',
      url=URL, author=AUTHOR, author_email=AUTHOR_EMAIL, license=LICENSE, classifiers=CLASSIFIERS,
      install_requires=['toolz'], python_requires=PYTHON_REQUIRES)
