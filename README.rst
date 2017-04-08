django-hierarkey -- Hierarchical key-value store
================================================

.. image:: https://img.shields.io/pypi/v/django-hierarkey.svg
   :target: https://pypi.python.org/pypi/django-hierarkey

.. image:: https://readthedocs.org/projects/django-hierarkey/badge/?version=latest
   :target: https://django-hierarkey.readthedocs.io/

.. image:: https://travis-ci.org/raphaelm/django-hierarkey.svg?branch=master
   :target: https://travis-ci.org/raphaelm/django-hierarkey

.. image:: https://codecov.io/gh/raphaelm/django-hierarkey/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/raphaelm/django-hierarkey

This package allows you to attach a key-value store to a model, e.g. to store preferences of
an user or a customer. The package supports arbitrary datatypes, defaults and model hierarchies,
i.e. you can define a different model instance as your instance's parent and the values of the
parent instance will be used as default values for the child instances.

This approach has been in use in `pretix`_ for quite a while, so it has been tested in
production.

Tested with Python 3.4-3.6 and Django 1.9-1.11.

License
-------
The code in this repository is published under the terms of the Apache License. 
See the LICENSE file for the complete license text.

This project is maintained by Raphael Michel <mail@raphaelmichel.de>. See the
AUTHORS file for a list of all the awesome folks who contributed to this project.

.. _pretix: https://github.com/pretix/pretix
