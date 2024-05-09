# -*- coding: utf-8 -*-

"""
Simplified Pxssh
"""

from __future__ import absolute_import, division, print_function

import logging
import subprocess

from pexpect import pxssh, spawn
#  from hexdump import hexdump

LOG = logging.getLogger(__name__)


class SimplifiedPxssh(pxssh.pxssh):

    def login(self, host, auto_prompt_reset=True):  # pylint: disable=arguments-differ
        """ Radically simplified login without the 'New certificate -- always accept it.' stuff."""

        self._original_host = host

        spawn._spawn(self, 'ssh', args=[host])  # pylint: disable=protected-access
        if not self.sync_original_prompt():
            self.close()
            raise pxssh.ExceptionPxssh('could not synchronize with original prompt')

        # We appear to be in.
        # Set shell prompt to something unique.
        if auto_prompt_reset:
            if not self.set_unique_prompt():
                self.close()
                raise pxssh.ExceptionPxssh('could not set shell prompt')

        return True

    def run_command(self, command):
        """ Run command and don’t expect any additional output."""

        #  self.logfile_read = io.StringIO()
        self.sendline(command)
        self.prompt()
        #  self.logfile_read.seek(0)
        #  output = self.logfile_read.read()
        #  print("+" + output + "+")

        #  print(hexdump(command.encode('utf-8')))
        #  print(hexdump(self.before.encode('utf-8')))
        len_ok = len(self.before) <= (len(command) + 6)
        output_end_ok = self.before.endswith(command + '\r\n')
        if not len_ok or not output_end_ok:
            raise Exception("Expected: '{}', Got: '{}'".format(
                command + '\n',
                self.before))

    def copy_to_remote(self, local_file_path, remote_file_path):
        with open(local_file_path, 'r') as local_file_fh:
            returncode = subprocess.call(
                ['ssh', self._original_host, 'cat', '>', remote_file_path],
                stdin=local_file_fh)
        if returncode != 0:
            raise Exception(
                'Could not put file {} on host {}.'.format(
                    local_file_path,
                    self._original_host,
                )
            )

    def get_platform(self):
        """Return our platform name 'linux_x86_64'

        Format based on PEP 425 Compatibility Tags (wheel/pep425tags.py).
        """

        #  return distutils.util.get_platform().replace('.', '_').replace('-', '_')

        self.sendline('uname -m')
        self.expect(r'[\w-]{3,20}\r\n')
        machine = self.after.strip()
        self.prompt()

        self.sendline('uname -s')
        self.expect(r'[\w-]{3,20}\r\n')
        osname = self.after.strip()
        self.prompt()

        return "{}_{}".format(osname, machine).replace('.', '_').replace('-', '_').lower()
