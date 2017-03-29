# -*- coding: utf-8 -*-

"""
Vault implementations
"""

from __future__ import absolute_import, division, print_function

import os
import logging
from abc import ABC, abstractmethod

from appdirs import user_config_dir

from .helpers import ensure_permissions

LOG = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods


class Vault(ABC):
    """ Abstract Vault class. """

    @abstractmethod
    def get_key(self, host, device_name):
        pass


class FileVault(Vault):
    """ Simple, file based Vault implementation. """

    def __init__(self):
        super(FileVault, self).__init__()

        # File layout copied/reused from borgbackup.
        self._keys_dir = os.path.join(user_config_dir(appname='fdeunlock'), 'keys')

        os.makedirs(self._keys_dir, exist_ok=True)  # pylint: disable=unexpected-keyword-arg
        ensure_permissions(self._keys_dir, 0o0700)

    def get_key(self, host, device_name):
        super(FileVault, self).get_key(host, device_name)

        key_path = os.path.join(self._keys_dir, '{}_{}.key'.format(host, device_name))
        LOG.debug("Trying to access key file: {}".format(key_path))
        try:
            with open(key_path, 'rb') as key_fh:
                return key_fh.read()
        except FileNotFoundError:
            return None
