Getting started
===============

Install hierarkey
-----------------

You only need to install the hierarkey package, for example using pip::

    $ pip install django-hierarkey

That's it!

Attach a storage to a single models
-----------------------------------

As a simple first example, we will attach a storage object to a single model.
For example, you could use this to store settings for every user.
If you want to use the hierarchical features of hierarkey, just skip to the next example.

First of all, in your ``models.py``, we will create a ``Hierarkey`` object::


    from hierarkey.models import Hierarkey

    hierarkey = Hierarkey(attribute_name='settings')

The attribute name defines the name that you will use later to access the storage.
This allows you to use multiple separated storage hierarchies within one model, if you want to.
Next, add a decorator to the model you want to associate the storage with::

    @hierarkey.add()
    class User(models.Model):
        ....

.. note:: The parentheses in the call to the ``@hierarkey.add()`` decorator are required.
          Refer to the :ref:`API documentation <api>` for more information on its parameters.s

Now, you need to create a database migration and apply it::

    $ python manage.py makemigrations
    $ python manage.py migrate

Build a hierarchical storage
----------------------------

To build a hierarchy, we need multiple models. In our example, we will have a three-level hierarchy,
consisting of global settings, organization settings and user settings. You can use more levels if you
want to or you can omit the global settings. There can only be one level of global settings.

As in the previous example, we first create a ``Hierarkey`` object::

    from hierarkey.models import GlobalSettingsBase, Hierarkey

    hierarkey = Hierarkey(attribute_name='settings')

Next, we define a class that we attach the global settings to. This class can be empty and is not needed
except for consistency in the hierarkey API. You can define it like this::

    @hierarkey.set_global()
    class GlobalSettings(GlobalSettingsBase):
        pass

Then, we add our other two layers. Note that the organization layer works the same way as the simple
example above, while the for the user model we specify the name of the field containing the foreign key
field refering to the parent object::

    @hierarkey.add()
    class Organization(models.Model):
        ...

    @hierarkey.add(parent_field='organization')
    class User(models.Model):
        organization = models.ForeignKey(Organization)
        ...

Now, you need to create a database migration and apply it::

    $ python manage.py makemigrations
    $ python manage.py migrate


Set default values
------------------

You can add default values by calling a method on the ``Hierarkey`` object specifying the key, the value
and the type::

    hierarkey.add_default('key', 'value', bool)

Access the settings storage
---------------------------

On an instance of your model, you can access the settings storage under the name you specified as the
``attribute_name`` further above.

You can read and write the values in the key-value store in three ways. First, by attribute access::

    print(user.settings.theme)
    user.settings.theme = 'dark'
    del user.settings.theme

Second, by item access::

    print(user.settings['theme'])
    user.settings['theme'] = 'dark'
    del user.settings['theme']

And third, using explicit methods::

    print(user.settings.get('theme'))
    user.settings.set('theme', 'dark')
    user.settings.delete('theme')

All changes are written to the database instantly, while values are read eagerly and are being cached.

Unserialization will only be automatically performed for keys that have a default value specified in code.
If you want to unserialize other keys, you need to use the explicit getter methods and specify the type
yourself::

    user.settings.get('theme', as_type=int)

To access the global settings, you can instantiate the global setttings class you defined before::

    GlobalSettings().settings.get(…)

Next steps
----------

You can now continue reading either about :ref:`forms` or in the :ref:`api`.