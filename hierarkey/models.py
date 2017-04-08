import sys
from collections import namedtuple
from typing import Any, Callable

from django.core.exceptions import ImproperlyConfigured
from django.db import models


class BaseHierarkeyStoreModel(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()

    class Meta:
        abstract = True


HierarkeyDefault = namedtuple('HierarkeyDefault', ['value', 'type'])
HierarkeyType = namedtuple('HierarkeyType', ['type', 'serialize', 'unserialize'])


class Hierarkey:
    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
        self.global_class = None
        self.defaults = {}
        self.types = []

    def _create_attrs(self, base_model: type) -> dict:
        class Meta:
            pass

        attrs = {
            'Meta': Meta,
            '__module__': base_model.__module__,
        }
        return attrs

    def _create_model(self, model_name: str, attrs: dict) -> type:
        return models.base.ModelBase(model_name, (BaseHierarkeyStoreModel,), attrs)

    def add_default(self, key: str, value: Any, default_type: type=str) -> None:
        self.defaults[key] = HierarkeyDefault(value, default_type)

    def add_type(self, type: type, serialize: Callable, unserialize: Callable) -> None:
        self.types.append(HierarkeyType(type=type, serialize=serialize, unserialize=unserialize))

    def add_global(self, cache_namespace: str=None) -> type:
        def wrapper(wrapped_class):
            if issubclass(wrapped_class, models.Model):
                raise ImproperlyConfigured('Hierarkey.add_global() can only be invoked on a normal class, '
                                           'not on a Django model.')

            _cache_namespace = cache_namespace or ('%s_%s' % (wrapped_class.__name__, self.attribute_name))

            attrs = self._create_attrs(wrapped_class)

            model_name = '%s_%sStore' % (wrapped_class.__name__, self.attribute_name.title())
            kv_model = self._create_model(model_name, attrs)

            def init(self, *args, object=None, **kwargs):
                super(kv_model, self).__init__(*args, **kwargs)

            setattr(kv_model, '__init__', init)

            hierarkey = self

            def prop(self):
                from .proxy import HierarkeyProxy

                return HierarkeyProxy(self,
                                      type=kv_model,
                                      hierarkey=hierarkey,
                                      cache_namespace=_cache_namespace)

            setattr(sys.modules[wrapped_class.__module__], model_name, kv_model)
            setattr(wrapped_class, '_%s_objects' % self.attribute_name, kv_model.objects)
            setattr(wrapped_class, self.attribute_name, property(prop))
            self.global_class = wrapped_class
            return wrapped_class

        return wrapper

    def add(self, cache_namespace: str=None, parent_field: str=None) -> type:
        def wrapper(model):
            if not issubclass(model, models.Model):
                raise ImproperlyConfigured('Hierarkey.add() can only be invoked on a Django model')

            _cache_namespace = cache_namespace or ('%s_%s' % (model.__name__, self.attribute_name))

            attrs = self._create_attrs(model)
            attrs['object'] = models.ForeignKey(model, related_name='_%s_objects' % self.attribute_name,
                                                on_delete=models.CASCADE)
            model_name = '%s_%sStore' % (model.__name__, self.attribute_name.title())
            kv_model = self._create_model(model_name, attrs)

            setattr(sys.modules[model.__module__], model_name, kv_model)

            hierarkey = self

            def prop(self):
                from .proxy import HierarkeyProxy

                try:
                    parent = getattr(self, parent_field) if parent_field else None
                except models.ObjectDoesNotExist:
                    parent = None

                if not parent and hierarkey.global_class:
                    parent = hierarkey.global_class()

                return HierarkeyProxy(self,
                                      type=kv_model,
                                      hierarkey=hierarkey,
                                      parent=parent,
                                      cache_namespace=_cache_namespace)

            setattr(model, self.attribute_name, property(prop))

            return model

        return wrapper


class GlobalSettingsBase:
    pk = '_global'
