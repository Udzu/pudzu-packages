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

setup(name='pudzu-pillar', version=VERSION, packages=find_namespace_packages(include=['pudzu.*']),
      description='Various imaging utilities, monkey-patched onto Pillow.',
      keywords='pudzu imaging pillow',
      url=URL, author=AUTHOR, author_email=AUTHOR_EMAIL, license=LICENSE, classifiers=CLASSIFIERS,
      install_requires=[f'pudzu-utils>={VERSION}', 'Pillow', 'numpy'], python_requires=PYTHON_REQUIRES)
