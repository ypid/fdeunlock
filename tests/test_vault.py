# vim: foldmarker=[[[,]]]:foldmethod=marker


import os
from unittest import mock

from nose.tools import (  # NOQA
    assert_equal,
    assert_not_equal,
    assert_raises_regexp,
    nottest,
)

from fdeunlock import vault

config_test_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'data', 'config', 'fdeunlock'
)

keys_test_dir = os.path.join(config_test_dir, 'keys')


class OsStat:
    def __init__(self, st_mode):
        self.st_mode = st_mode


class Test:

    @mock.patch('fdeunlock.vault.ensure_permissions', autospec=True)
    @mock.patch('fdeunlock.vault.user_config_dir', return_value=config_test_dir, autospec=True)
    def test_file_vault_init(self, mock_user_config_dir, ensure_permissions):
        vault.FileVault()
        ensure_permissions.assert_called_once_with(keys_test_dir, 0o0700)

    @mock.patch('fdeunlock.vault.user_config_dir', return_value=config_test_dir, autospec=True)
    def test_file_vault_get_key(self, mock_user_config_dir):
        v = vault.FileVault()
        assert_equal(v.get_key('fde.example.org', 'sda3_crypt'), b'testkey')
