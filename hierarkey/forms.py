import logging

from django import forms
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class SettingsForm(forms.Form):
    BOOL_CHOICES = (
        ('False', _('disabled')),
        ('True', _('enabled')),
    )

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('object', None)
        kwargs['initial'] = self.obj.settings.freeze()
        super().__init__(*args, **kwargs)

    def save(self):
        """
        Performs the save operation
        """
        for name, field in self.fields.items():
            value = self.cleaned_data[name]
            if isinstance(value, UploadedFile):
                # Delete old file
                fname = self.obj.settings.get(name, as_type=File)
                if fname:
                    try:
                        default_storage.delete(fname.name)
                    except OSError:
                        logger.error('Deleting file %s failed.' % fname.name)

                # Create new file
                nonce = get_random_string(length=8)
                # TODO: Configurable directory structure
                fname = '%s/%s.%s.%s' % (self.obj.pk, name, nonce, value.name.split('.')[-1])
                newname = default_storage.save(fname, value)
                value._name = newname
                self.obj.settings.set(name, value)
            elif isinstance(value, File):
                # file is unchanged
                continue
            elif isinstance(field, forms.FileField):
                # file is deleted
                fname = self.obj.settings.get(name, as_type=File)
                if fname:
                    try:
                        default_storage.delete(fname.name)
                    except OSError:
                        logger.error('Deleting file %s failed.' % fname.name)
                del self.obj.settings[name]
            elif value is None:
                del self.obj.settings[name]
            elif self.obj.settings.get(name, as_type=type(value)) != value:
                self.obj.settings.set(name, value)
