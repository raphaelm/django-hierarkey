from datetime import date, datetime, time
from decimal import Decimal
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import now

from hierarkey.models import HierarkeyDefault

from .testapp.models import GlobalSettings, Organization, User, hierarkey


class MyType:
    def __init__(self, foo):
        self.foo = foo

    def __eq__(self, other):
        return self.foo == other.foo


class SettingsTestCase(TestCase):
    def setUp(self):
        hierarkey.add_default('test_default', 'def', str)
        self.global_settings = GlobalSettings()
        self.global_settings.settings.flush()
        self.organization = Organization.objects.create(name='Dummy')
        self.organization.settings.flush()
        self.user = User.objects.create(
            organization=self.organization, name='Dummy'
        )
        self.user.settings.flush()

    def test_global_set_explicit(self):
        self.global_settings.settings.test = 'foo'
        self.assertEqual(self.global_settings.settings.test, 'foo')

        # Reload object
        self.global_settings = GlobalSettings()
        self.assertEqual(self.global_settings.settings.test, 'foo')

    def test_organization_set_explicit(self):
        self.organization.settings.test = 'foo'
        self.assertEqual(self.organization.settings.test, 'foo')

        # Reload object
        self.organization = Organization.objects.get(pk=self.organization.pk)
        self.assertEqual(self.organization.settings.test, 'foo')

    def test_user_set_explicit(self):
        self.user.settings.test = 'foo'
        self.assertEqual(self.user.settings.test, 'foo')

        # Reload object
        self.user = User.objects.get(pk=self.user.pk)
        self.assertEqual(self.user.settings.test, 'foo')

    def test_user_set_twice(self):
        self.user.settings.test = 'bar'
        self.user.settings.test = 'foo'
        self.assertEqual(self.user.settings.test, 'foo')

        # Reload object
        self.user = User.objects.get(pk=self.user.pk)
        self.assertEqual(self.user.settings.test, 'foo')

    def test_organization_set_on_global(self):
        self.global_settings.settings.test = 'foo'
        self.assertEqual(self.global_settings.settings.test, 'foo')
        self.assertEqual(self.organization.settings.test, 'foo')

        # Reload object
        self.global_settings = GlobalSettings()
        self.assertEqual(self.global_settings.settings.test, 'foo')
        self.assertEqual(self.organization.settings.test, 'foo')

    def test_user_set_on_global(self):
        self.global_settings.settings.test = 'foo'
        self.assertEqual(self.global_settings.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'foo')

        # Reload object
        self.global_settings = GlobalSettings()
        self.assertEqual(self.global_settings.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'foo')

    def test_user_set_on_organization(self):
        self.organization.settings.test = 'foo'
        self.assertEqual(self.organization.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'foo')

        # Reload object
        self.organization = Organization.objects.get(id=self.organization.id)
        self.assertEqual(self.organization.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'foo')

    def test_user_override_organization(self):
        self.organization.settings.test = 'foo'
        self.user.settings.test = 'bar'
        self.assertEqual(self.organization.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'bar')

        # Reload object
        self.organization = Organization.objects.get(id=self.organization.id)
        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.organization.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'bar')

    def test_user_override_global(self):
        self.global_settings.settings.test = 'foo'
        self.user.settings.test = 'bar'
        self.assertEqual(self.global_settings.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'bar')

        # Reload object
        self.global_settings = GlobalSettings()
        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.global_settings.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'bar')

    def test_default(self):
        self.assertEqual(self.global_settings.settings.test_default, 'def')
        self.assertEqual(self.organization.settings.test_default, 'def')
        self.assertEqual(self.user.settings.test_default, 'def')
        self.assertEqual(self.user.settings.get('nonexistant', default='abc'), 'abc')

    def test_default_typing(self):
        self.assertIs(type(self.user.settings.get('nonexistant', as_type=Decimal, default=0)), Decimal)

    def test_item_access(self):
        self.user.settings['foo'] = 'abc'
        self.assertEqual(self.user.settings['foo'], 'abc')
        del self.user.settings['foo']
        self.assertIsNone(self.user.settings['foo'])

    def test_delete(self):
        self.organization.settings.test = 'foo'
        self.user.settings.test = 'bar'
        self.global_settings.settings.testglobal = 'baz'
        self.assertEqual(self.organization.settings.test, 'foo')
        self.assertEqual(self.user.settings.test, 'bar')
        self.assertEqual(self.global_settings.settings.testglobal, 'baz')

        del self.user.settings.test
        self.assertEqual(self.user.settings.test, 'foo')

        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.user.settings.test, 'foo')

        del self.organization.settings.test
        self.assertIsNone(self.organization.settings.test)

        self.organization = Organization.objects.get(id=self.organization.id)
        self.assertIsNone(self.organization.settings.test)

        del self.global_settings.settings.testglobal
        self.global_settings = GlobalSettings()
        self.assertIsNone(self.global_settings.settings.testglobal)

    def test_serialize_str(self):
        self._test_serialization('ABC', as_type=str)

    def test_serialize_float(self):
        self._test_serialization(2.3, float)

    def test_serialize_int(self):
        self._test_serialization(2, int)

    def test_serialize_datetime(self):
        self._test_serialization(now(), datetime)

    def test_serialize_time(self):
        self._test_serialization(now().time(), time)

    def test_serialize_date(self):
        self._test_serialization(now().date(), date)

    def test_serialize_decimal(self):
        self._test_serialization(Decimal('2.3'), Decimal)

    def test_serialize_dict(self):
        self._test_serialization({'a': 'b', 'c': 'd'}, dict)

    def test_serialize_list(self):
        self._test_serialization([1, 2, 'a'], list)

    def test_serialize_bool(self):
        self._test_serialization(True, bool)
        self._test_serialization(False, bool)

    def test_serialize_bool_implicit(self):
        self.user.settings.set('test', True)
        self.user.settings.flush()
        self.assertIs(self.user.settings.get('test', as_type=None), True)
        self.user.settings.set('test', False)
        self.user.settings.flush()
        self.assertIs(self.user.settings.get('test', as_type=None), False)

    def test_serialize_model(self):
        self._test_serialization(self.user, User)

    def test_serialize_custom_type(self):
        hierarkey.add_type(MyType, lambda v: v.foo, lambda v: MyType(v))
        self._test_serialization(MyType('bar'), MyType)

    def test_custom_type_default(self):
        hierarkey.add_type(MyType, lambda v: v.foo, lambda v: MyType(v))
        hierarkey.add_default('mytype_foo', 'bar', MyType)
        self.assertEqual(self.user.settings.get('mytype_foo'), MyType('bar'))
        self.user.settings.set('mytype_foo', MyType('baz'))
        self.user.settings.flush()
        self.assertEqual(self.user.settings.get('mytype_foo'), MyType('baz'))

    def test_serialize_unknown(self):
        class Type:
            pass

        try:
            self._test_serialization(Type(), Type)
            self.assertTrue(False, 'No exception thrown!')
        except TypeError:
            pass

    def test_serialize_file(self):
        val = SimpleUploadedFile("sample_invalid_image.jpg", b"file_content", content_type="image/jpeg")
        default_storage.save(val.name, val)
        val.close()
        self.user.settings.set('test', val)
        self.user.settings.flush()
        f = self.user.settings.get('test', as_type=File)
        self.assertIsInstance(f, File)
        self.assertTrue(f.name.endswith(val.name))
        f.close()

    def test_unserialize_file_value(self):
        val = SimpleUploadedFile("sample_invalid_image.jpg", b"file_content", content_type="image/jpeg")
        default_storage.save(val.name, val)
        val.close()
        self.user.settings.set('test', val)
        self.user.settings.flush()
        f = self.user.settings.get('test', as_type=File)
        self.assertIsInstance(f, File)
        self.assertTrue(f.name.endswith(val.name))
        f.close()

    def test_autodetect_file_value(self):
        val = SimpleUploadedFile("sample_invalid_image.jpg", b"file_content", content_type="image/jpeg")
        default_storage.save(val.name, val)
        val.close()
        self.user.settings.set('test', val)
        self.user.settings.flush()
        f = self.user.settings.get('test')
        self.assertIsInstance(f, File)
        self.assertTrue(f.name.endswith(val.name))
        f.close()

    def test_autodetect_file_value_of_parent(self):
        val = SimpleUploadedFile("sample_invalid_image.jpg", b"file_content", content_type="image/jpeg")
        default_storage.save(val.name, val)
        val.close()
        self.organization.settings.set('test', val)
        self.organization.settings.flush()
        f = self.user.settings.get('test')
        self.assertIsInstance(f, File)
        self.assertTrue(f.name.endswith(val.name))
        f.close()

    def test_nonexistant_file(self):
        self.organization.settings.set('test', 'file://foo')
        self.organization.settings.flush()
        f = self.user.settings.get('test', as_type=File)
        self.assertIs(f, False)

    def _test_serialization(self, val, as_type):
        self.user.settings.set('test', val)
        self.user.settings.flush()
        self.assertEqual(self.user.settings.get('test', as_type=as_type), val)
        self.assertIsInstance(self.user.settings.get('test', as_type=as_type), as_type)

    def test_freeze(self):
        olddef = hierarkey.defaults
        hierarkey.defaults = {
            'test_default': HierarkeyDefault(value='def', type=str)
        }
        self.user.organization.settings.set('bar', 'baz')
        self.user.organization.settings.set('foo', 'baz')
        self.user.settings.set('foo', 'bar')
        frozen = self.user.settings.freeze()
        self.user.settings.set('foo', 'notfrozen')

        try:
            self.assertEqual(frozen, {
                'test_default': 'def',
                'bar': 'baz',
                'foo': 'bar'
            })
        finally:
            hierarkey.defaults = olddef
