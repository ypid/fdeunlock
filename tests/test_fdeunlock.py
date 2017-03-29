# -*- coding: utf-8 -*-
# vim: foldmarker=[[[,]]]:foldmethod=marker

from __future__ import absolute_import, division, print_function

from nose.tools import *  # NOQA

from fdeunlock import vault
from fdeunlock import fdeunlock


class Test():

    def test_instantiate_fdeunlock(self):
        fdeunlock.FdeUnlock(vault=vault.FileVault())
