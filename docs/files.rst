.. _files:

File handling
=============

Hierarkey has rudimentary support of saving a ``file`` into the key-value storage. In this case, not the *content*
of the file will be saved in the key-value store. Instead, only the *name* of the file within the configured Django
storage backend will be saved.

You need to save the file to the storage backend yourself and then pass the ``File`` object to hierarkey.
When you access the key in the store, the ``file://`` prefix will automatically be detected and hierarkey will use
your default storage backend to open the file for you. The ``binary_file`` flag of the ``get()`` method allows you to
open the file in binary mode.

When you use our :ref:`forms support <forms>`, this is done automatically for you. You can just specify a
normal ``django.forms.FileField`` field on the model and ``HierarkeyForm`` will deal with storing the file
to the default storage backend as well as deleting and replacing files. The filename will be automatically generated
based on the primary key of your model, the key in the storage, and a random nonce. You can change this behaviour by
overriding :py:meth:`get_new_filename() <hierarkey.forms.HierarkeyForm.get_new_filename>` on your form.