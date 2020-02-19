from django.db import models
from django.utils.translation import gettext_lazy as _

from hierarkey.models import GlobalSettingsBase, Hierarkey

hierarkey = Hierarkey(attribute_name='settings')


@hierarkey.set_global(cache_namespace='global')
class GlobalSettings(GlobalSettingsBase):
    pass


@hierarkey.add(cache_namespace='organization')
class Organization(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=190)

    def __str__(self):
        return self.name


@hierarkey.add(cache_namespace='user', parent_field='organization')
class User(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=190)
    organization = models.ForeignKey(Organization)

    def __str__(self):
        return str(self.name)
