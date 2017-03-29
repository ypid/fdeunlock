# -*- coding: utf-8 -*-
# vim: foldmarker=[[[,]]]:foldmethod=marker

from __future__ import absolute_import, division, print_function

import logging
from unittest import mock

from nose.tools import assert_equal, assert_not_equal, assert_raises_regexp, nottest  # NOQA
from testfixtures import log_capture

from fdeunlock import helpers


class OsStat(object):
    def __init__(self, st_mode):
        setattr(self, 'st_mode', st_mode)


class Test():

    @mock.patch('os.chmod', autospec=True)
    @mock.patch('os.stat', return_value=OsStat(0o40777), autospec=True)
    @log_capture()
    def test_ensure_permissions(self, os_stat, os_chmod, log):
        helpers.ensure_permissions('/tmp/test', 0o0600)
        os_stat.assert_called_with('/tmp/test')
        os_chmod.assert_called_with('/tmp/test', 0o0600)
        log.check(
            ('fdeunlock.helpers', 'INFO', 'Changed permissions of "/tmp/test" from 0777 to 0600.')
        )

    @mock.patch('os.chmod', autospec=True)
    @mock.patch('os.stat', return_value=OsStat(0o40700), autospec=True)
    @log_capture(level=logging.WARNING)
    def test_ensure_permissions_no_change(self, os_stat, os_chmod, log):
        helpers.ensure_permissions('/tmp/test', 0o40700)
        os_stat.assert_called_with('/tmp/test')
        assert_equal(os_chmod.call_count, 0)
        log.check()
