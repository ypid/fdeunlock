# -*- coding: utf-8 -*-
# vim: foldmarker=[[[,]]]:foldmethod=marker

# flake8: noqa

from __future__ import absolute_import, division, print_function

from nose.tools import *  # NOQA

from fdeunlock import checker


class Test():

    @raises(TypeError)
    def test_instantiate_abc(self):
        checker.HostChecker()
