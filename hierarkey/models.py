import sys
from django.db import models


class BaseHierarkeyModel(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()

    class Meta:
        abstract = True


def add_hierarkey_store(attribute_name='hkstore', cache_namespace=None, parent_field=None):
    def wrapper(model):
        _cache_namespace = cache_namespace or ('%s_%s' % (model.__name__, attribute_name))

        class Meta:
            pass

        attrs = {
            'Meta': Meta,
            'object': models.ForeignKey(model, related_name='_%s_objects' % attribute_name, on_delete=models.CASCADE),
            '__module__': model.__module__,
        }

        model_name = '%s_%sStore' % (model.__name__, attribute_name.title())
        kv_model = models.base.ModelBase(model_name, (BaseHierarkeyModel,), attrs)

        setattr(sys.modules[model.__module__], model_name, kv_model)
        setattr(model, '_%s_parent_field' % attribute_name, parent_field)
        setattr(model, '_%s_cache_namespace' % attribute_name, _cache_namespace)

        def prop(self):
            from .proxy import HierarkeyProxy

            try:
                return HierarkeyProxy(self,
                                      type=kv_model,
                                      parent=getattr(self, parent_field) if parent_field else None,
                                      cache_namespace=cache_namespace,
                                      attribute_name=attribute_name)
            except models.ObjectDoesNotExist:
                # Should only happen when creating new events
                return HierarkeyProxy(self,
                                      type=kv_model,
                                      cache_namespace=cache_namespace,
                                      attribute_name=attribute_name)

        setattr(model, attribute_name, property(prop))

        return model

    return wrapper


class GlobalHierarkeyStore(BaseHierarkeyModel):

    def __init__(self, *args, object=None, **kwargs):
        super().__init__(*args, **kwargs)
