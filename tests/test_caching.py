from django.db import transaction
from django.test import TransactionTestCase
from multiprocessing.pool import ThreadPool

from .testapp.models import GlobalSettings, hierarkey


class SettingsTestCase(TransactionTestCase):
    def setUp(self):
        self.pool = ThreadPool(processes=1)
        hierarkey.add_default('test_default', 'def', str)
        self.global_settings = GlobalSettings()
        self.global_settings.settings.flush()
        # The other test files do not use TransactionTestCase, so we need to manually clean up
        self.global_settings.settings._invalidate_cache_after_transaction()

    def tearDown(self):
        self.pool.close()

    def test_subsequent_read_uses_cache(self):
        with self.assertNumQueries(1):
            assert self.global_settings.settings.test_default == 'def'

        with self.assertNumQueries(0):
            assert self.global_settings.settings.test_default == 'def'
            gl2 = GlobalSettings()
            assert gl2.settings.test_default == 'def'

    def test_flush_cache(self):
        with self.assertNumQueries(1):
            assert self.global_settings.settings.test_default == 'def'

        with self.assertNumQueries(1):
            self.global_settings.settings.flush()
            assert self.global_settings.settings.test_default == 'def'

    def _get_value(self, key):
        global_settings = GlobalSettings()
        return global_settings.settings.get(key)

    def test_do_not_flush_before_transaction(self):
        with transaction.atomic():
            self.global_settings.settings.test_default = 'foo'

            # New value visible in same transaction
            assert self.global_settings.settings.test_default == 'foo'

            # Other thread cannot see default yet
            assert self.global_settings.settings.test_default == 'foo'
            t = self.pool.apply_async(self._get_value, ("test_default",))
            assert t.get() == 'def'

        # After the commit, all threads can see it
        assert self.global_settings.settings.test_default == 'foo'
        t = self.pool.apply_async(self._get_value, ("test_default",))
        assert t.get() == 'foo'

    def test_repeatable_read_within_transaction_without_cache_poisoning(self):
        with transaction.atomic():
            self.global_settings.settings.test_default = 'foo'

            # New value visible in same transaction
            assert self.global_settings.settings.test_default == 'foo'

            # Even on new object without local cache
            gs2 = GlobalSettings()
            assert gs2.settings.test_default == 'foo'

            # Other thread can still not see default yet
            assert self.global_settings.settings.test_default == 'foo'
            t = self.pool.apply_async(self._get_value, ("test_default",))
            assert t.get() == 'def'

        # After the commit, all threads can see it
        assert self.global_settings.settings.test_default == 'foo'
        assert gs2.settings.test_default == 'foo'
        t = self.pool.apply_async(self._get_value, ("test_default",))
        assert t.get() == 'foo'
