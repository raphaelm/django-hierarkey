.. _forms:

Forms
=====

Hierarkey provides a form base class that makes it really easy to manipulate values of a key-value store.
You just define your form as you normally would::

    from django import forms
    from hierarkey.forms import HierarkeyForm

    class MySettingsForm(HierarkeyForm):
        theme = forms.ChoiceField(
            choices=(('light', 'light'), ('dark', 'dark')
        )
        ...

You can use any form field that results in a data type that can be serialized and unserialized by hierarkey.
This includes most form fields defined by Django and even :ref:`custom types <customtype>`.

To save the data, you cann call the ``save()`` method on the form.
Note that the form takes two additional arguments to instantiate it, the object that you want to update the values for
(i.e. a ``GlobalSettings`` object or a model instance) and the ``attribute_name`` the storage is located at.
When using a class-based ``FormView``, you could integrate it like this::


    from django.views.generic import FormView

    class MySettingsView(FormView):
        form_class = MySettingsForm

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['attribute_name'] = 'settings'
            kwargs['obj'] = User.objects.get(...)
            return kwargs

        def form_valid(self, form):
            form.save()
            return super().form_valid(form)

.. note:: Initial values for the form will be taken from the settings storage, i.e. from the given object and the
          global and hardcoded defaults. Initial values set directly on the form or field layer are not supported.
