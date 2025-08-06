Migrate from 1.x to 2.x
=======================

django-hierarkey 1.x contained a bug in the data model:
A unique key on the combination of target object and configuration key was missing, causing storage of inconsistent data.
This was never a problem for us in practice, as the most recent entry always wins, but still requires fixing because it might become a problem in the future.

To upgrade from 1.x to 2.x, first increase your dependency version number or install the new version using pip::

    $ pip install "django-hierarkey==2.*"

Then, instruct Django to create the new required migrations::

    $ python manage.py makemigrations pretixbase
    Migrations for 'pretixbase':
      pretix/base/migrations/0284_alter_event_settingsstore_unique_together_and_more.py
        - Alter unique_together for event_settingsstore (1 constraint(s))
        - Alter unique_together for globalsettingsobject_settingsstore (1 constraint(s))
        - Alter unique_together for organizer_settingsstore (1 constraint(s))

Now, the resulting migration will look similar to this::

    from django.db import migrations


    class Migration(migrations.Migration):
        dependencies = [
            ("pretixbase", "0283_taxrule_default_taxrule_backfill"),
        ]

        operations = [
            migrations.AlterUniqueTogether(
                name="event_settingsstore",
                unique_together={("object", "key")},
            ),
            migrations.AlterUniqueTogether(
                name="globalsettingsobject_settingsstore",
                unique_together={("key",)},
            ),
            migrations.AlterUniqueTogether(
                name="organizer_settingsstore",
                unique_together={("object", "key")},
            ),
        ]

This migration will only be possible to apply if you ahve not been affected by the bug and you do not have a single
affected. To make the migration robust, you need to insert a cleanup step before creation of the unique key. In our
example above, the migration would be modified like this::

     from django.db import migrations
    +from hierarkey.utils import CleanHierarkeyDuplicates


     class Migration(migrations.Migration):

         dependencies = [
             ("pretixbase", "0283_taxrule_default_taxrule_backfill"),
         ]

         operations = [
    +        CleanHierarkeyDuplicates("Event_SettingsStore"),
    +        CleanHierarkeyDuplicates("GlobalSettingsObject_SettingsStore"),
    +        CleanHierarkeyDuplicates("Organizer_SettingsStore"),
             migrations.AlterUniqueTogether(
                 name="event_settingsstore",
                 unique_together={("object", "key")},
             ),
             migrations.AlterUniqueTogether(
                 name="globalsettingsobject_settingsstore",
                 unique_together={("key",)},
             ),
             migrations.AlterUniqueTogether(
                 name="organizer_settingsstore",
                 unique_together={("object", "key")},
             ),
         ]
