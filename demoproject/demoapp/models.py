from django.db import models
from django.utils.translation import ugettext_lazy as _

from hierarkey.models import add_hierarkey_store


@add_hierarkey_store(attribute_name='settings', cache_namespace='organization')
class Organization(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=190)

    def __str__(self):
        return self.name


@add_hierarkey_store(attribute_name='settings', cache_namespace='user', parent_field='organization')
class User(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=190)
    organization = models.ForeignKey(Organization)

    def __str__(self):
        return str(self.name)
