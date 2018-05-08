"""Event Magic Setup file."""


from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='eventmagic',
    version='0.1.14',
    description='Event scheduling with persistence for short-lived processes \
i.e. AWS Lambda',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/soimafreak/eventmagic',
    author='Matthew Smith',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Software Development :: Libraries :: Python Modules',
        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
    ],

    keywords='scheduling events lambda mysql',

    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'example.py']),
    install_requires=[
        'crontab==0.22.0',
        'mysql-connector-python==8.0.11'
    ],

    extras_require={
        'dev': [
            'flake8',
            'flake8-docstrings',
            'mock',
            'pytest',
            'pytest-cov',
            'setuptools>=38.6.0',
            'sphinx==1.5.5',
            'twine',
            'wheel'
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/soimafreak/eventmagic/issues',
        'Source': 'https://github.com/soimafreak/eventmagic/',
    },
)
