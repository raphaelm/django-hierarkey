django-hierarkey
================

.. image:: https://img.shields.io/pypi/v/django-hierarkey.svg
   :target: https://pypi.python.org/pypi/django-hierarkey

.. image:: https://travis-ci.org/raphaelm/django-hierarkey.svg?branch=master
   :target: https://travis-ci.org/raphaelm/django-hierarkey

.. image:: https://codecov.io/gh/raphaelm/django-hierarkey/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/raphaelm/django-hierarkey

This package allows you to attach a key-value store to a model, e.g. to store preferences of
an user or a customer. The package supports arbitrary datatypes, defaults and model hierarchies,
i.e. you can define a different model instance as your instance's parent and the values of the
parent instance will be used as default values for the child instances.

Documentation content
---------------------

.. toctree::
   :maxdepth: 1

   concept
   quickstart
   api
   forms
   exttype
   files

Author and License
------------------

This package has been created by Raphael Michel and is published under the terms of the Apache License 2.0.

.. _pretix: https://github.com/pretix/pretix
.. _django: https://www.djangoproject.com/
