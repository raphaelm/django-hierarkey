import pytest
from django.core.exceptions import ImproperlyConfigured

from .testapp.models import GlobalSettings, User, hierarkey


def test_global_settings_on_invalid():
    with pytest.raises(ImproperlyConfigured):
        hierarkey.set_global()(object)


def test_global_settings_on_model():
    with pytest.raises(ImproperlyConfigured):
        hierarkey.set_global()(User)


def test_model_settings_on_non_model():
    with pytest.raises(ImproperlyConfigured):
        hierarkey.add()(GlobalSettings)


def test_missing_parantheses():
    with pytest.raises(ImproperlyConfigured):
        hierarkey.set_global(GlobalSettings)

    with pytest.raises(ImproperlyConfigured):
        hierarkey.add(User)
