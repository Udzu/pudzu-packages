from setuptools import setup

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

setup(name='pudzu-utils', version=VERSION, packages=['pudzu.utils'],
      description='Various utility functions and data structures used by the other pudzu packages.',
      keywords='pudzu utilities',
      url=URL, author=AUTHOR, author_email=AUTHOR_EMAIL, license=LICENSE, classifiers=CLASSIFIERS,
      install_requires=['toolz'], python_requires=PYTHON_REQUIRES)

setup(name='pudzu-dates', version=VERSION, packages=['pudzu.dates'],
      description='Date classes supporting flexible calendars, date deltas and ranges.',
      keywords='pudzu date calendar',
      url=URL, author=AUTHOR, author_email=AUTHOR_EMAIL, license=LICENSE, classifiers=CLASSIFIERS,
      install_requires=[f'pudzu-utils>={VERSION}'], python_requires=PYTHON_REQUIRES)

setup(name='pudzu-pillar', version=VERSION, packages=['pudzu.pillar'],
      description='Various imaging utilities, monkey-patched onto Pillow.',
      keywords='pudzu imaging pillow',
      url=URL, author=AUTHOR, author_email=AUTHOR_EMAIL, license=LICENSE, classifiers=CLASSIFIERS,
      install_requires=[f'pudzu-utils>={VERSION}', 'Pillow', 'numpy'], python_requires=PYTHON_REQUIRES)

setup(name='pudzu-charts', version=VERSION, packages=['pudzu.charts'],
      description='Pillow-based charting tools.',
      keywords='pudzu charts pillow',
      url=URL, author=AUTHOR, author_email=AUTHOR_EMAIL, license=LICENSE, classifiers=CLASSIFIERS,
      install_requires=[f'pudzu-pillar>={VERSION}', f'pudzu-dates>={VERSION}', 'pandas'], python_requires=PYTHON_REQUIRES)
