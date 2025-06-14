from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
try:
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''

try:
    from hierarkey import version
except ImportError:
    version = '?'

setup(
    name='django-hierarkey',
    version=version,
    description='Hierarchical key-value store for django',
    long_description=long_description,
    url='https://github.com/raphaelm/django-hierarkey',
    author='Raphael Michel',
    author_email='mail@raphaelmichel.de',
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
    ],

    keywords='strings database models keyvalue',
    install_requires=[
        'python-dateutil'
    ],

    packages=find_packages(exclude=['tests', 'tests.*', 'demoproject', 'demoproject.*']),
    include_package_data=True,
)
