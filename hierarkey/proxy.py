import decimal
import json
from datetime import date, datetime, time
from typing import Any, Dict, Optional

import dateutil.parser
from django.core.cache import cache
from django.core.files import File
from django.core.files.storage import default_storage
from django.db.models import Model

from hierarkey.models import Hierarkey


class HierarkeyProxy:
    def __init__(self, obj: Model, hierarkey: Hierarkey, cache_namespace: str, parent: Optional[Model] = None,
                 type: type=None):
        self._obj = obj
        self._h = hierarkey
        self._cache_namespace = cache_namespace
        self._parent = parent
        self._cached_obj = None
        self._write_cached_obj = None
        self._type = type

    @property
    def _objects(self):
        return getattr(self._obj, '_%s_objects' % self._h.attribute_name)

    def _cache(self) -> Dict[str, Any]:
        if self._cached_obj is None:
            self._cached_obj = cache.get_or_set(
                'hierarkey_{}_{}'.format(self._cache_namespace, self._obj.pk),
                lambda: {s.key: s.value for s in self._objects.all()},
                timeout=1800
            )
        return self._cached_obj

    def _write_cache(self) -> Dict[str, Any]:
        if self._write_cached_obj is None:
            self._write_cached_obj = {
                s.key: s for s in self._objects.all()
            }
        return self._write_cached_obj

    def _flush(self) -> None:
        self._cached_obj = None
        self._write_cached_obj = None
        self._flush_external_cache()

    def _flush_external_cache(self):
        cache.delete('hierarkey_{}_{}'.format(self._cache_namespace, self._obj.pk))

    def freeze(self) -> dict:
        """
        Returns a dictionary of all settings set for this object, including
        any default values of its parents or hardcoded in pretix.
        """
        settings = {}
        for key, v in self._h.defaults.items():
            settings[key] = self._unserialize(v.value, v.type)
        if self._parent:
            settings.update(getattr(self._parent, self._h.attribute_name).freeze())
        for key in self._cache():
            settings[key] = self.get(key)
        return settings

    def _unserialize(self, value: str, as_type: type, binary_file=False) -> Any:
        if as_type is None and value is not None and value.startswith('file://'):
            as_type = File

        if as_type is not None and isinstance(value, as_type):
            return value
        elif value is None:
            return None
        elif as_type == int or as_type == float or as_type == decimal.Decimal:
            return as_type(value)
        elif as_type == dict or as_type == list:
            return json.loads(value)
        elif as_type == bool or value in ('True', 'False'):
            return value == 'True'
        elif as_type == File:
            try:
                fi = default_storage.open(value[7:], 'rb' if binary_file else 'r')
                fi.url = default_storage.url(value[7:])
                return fi
            except OSError:
                return False
        elif as_type == datetime:
            return dateutil.parser.parse(value)
        elif as_type == date:
            return dateutil.parser.parse(value).date()
        elif as_type == time:
            return dateutil.parser.parse(value).time()
        elif as_type is not None:
            for t in self._h.types:
                if issubclass(as_type, t.type):
                    return t.unserialize(value)

        if as_type is not None and issubclass(as_type, Model):
            return as_type.objects.get(pk=value)

        return value

    def _serialize(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, int) or isinstance(value, float) \
                or isinstance(value, bool) or isinstance(value, decimal.Decimal):
            return str(value)
        elif isinstance(value, list) or isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, datetime) or isinstance(value, date) or isinstance(value, time):
            return value.isoformat()
        elif isinstance(value, Model):
            return value.pk
        elif isinstance(value, File):
            return 'file://' + value.name
        else:
            for t in self._h.types:
                if isinstance(value, t.type):
                    return t.serialize(value)

        raise TypeError('Unable to serialize %s into a setting.' % str(type(value)))

    def get(self, key: str, default=None, as_type: type = None, binary_file=False):
        """
        Get a setting specified by key ``key``. Normally, settings are strings, but
        if you put non-strings into the settings object, you can request unserialization
        by specifying ``as_type``. If the key does not have a harcdoded type in the pretix source,
        omitting ``as_type`` always will get you a string.

        If the setting with the specified name does not exist on this object, any parent object
        will be queried (e.g. the organizer of an event). If still no value is found, a default
        value hardcoded will be returned if one exists. If not, the value of the ``default`` argument
        will be returned instead.
        """
        if as_type is None and key in self._h.defaults:
            as_type = self._h.defaults[key].type

        if key in self._cache():
            value = self._cache()[key]
        else:
            value = None
            if self._parent:
                value = getattr(self._parent, self._h.attribute_name).get(key, as_type=str)
            if value is None and key in self._h.defaults:
                value = self._h.defaults[key].value
            if value is None and default is not None:
                value = default

        return self._unserialize(value, as_type, binary_file=binary_file)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __getattr__(self, key: str) -> Any:
        if key.startswith('_'):
            return super().__getattribute__(key)
        return self.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith('_'):
            return super().__setattr__(key, value)
        self.set(key, value)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def set(self, key: str, value: Any) -> None:
        """
        Stores a setting to the database of its object.
        """
        wc = self._write_cache()
        if key in wc:
            s = wc[key]
        else:
            s = self._type(object=self._obj, key=key)
        s.value = self._serialize(value)
        s.save()
        self._cache()[key] = s.value
        wc[key] = s
        self._flush_external_cache()

    def __delattr__(self, key: str) -> None:
        if key.startswith('_'):
            return super().__delattr__(key)
        self.delete(key)

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    def delete(self, key: str) -> None:
        """
        Deletes a setting from this object's storage.
        """
        if key in self._write_cache():
            self._write_cache()[key].delete()
            del self._write_cache()[key]

        if key in self._cache():
            del self._cache()[key]

        self._flush_external_cache()
