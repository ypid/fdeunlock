# -*- coding: utf-8 -*-

"""
Core of FDEunlock
"""

from __future__ import absolute_import, division, print_function

import os
import re
import logging
import time
import socket
import subprocess
from getpass import getpass

from pexpect.exceptions import ExceptionPexpect

from .helpers import read_config, read_properties_config, write_properties_config, \
    read_ssh_config, get_user_dir
from .checker import NetworkBasedChecker, SshBasedChecker, CheckViolation
from .pxssh import SimplifiedPxssh

LOG = logging.getLogger(__name__)


class FdeUnlock(object):

    def __init__(self, vault, checkers=None):

        self._vault = vault
        self._checkers = []
        if checkers is not None:
            self._checkers = checkers

        self._data_dir = get_user_dir('data')
        os.makedirs(self._data_dir, exist_ok=True)  # pylint: disable=unexpected-keyword-arg

        self._cfg = read_config()
        self._properties = read_properties_config()
        self._ssh_cfg = read_ssh_config()

    def check_and_unlock(self, host, unlock=True):

        self._original_host = host

        if not self._cfg.has_section(self._original_host):
            self._cfg.add_section(self._original_host)
        if not self._properties.has_section(self._original_host):
            self._properties.add_section(self._original_host)

        ssh_host_cfg = self._ssh_cfg.lookup(self._original_host)
        self._address_family = self._cfg.get(
            self._original_host, 'address_family',
            fallback=ssh_host_cfg.get('addressfamily', 'any'))

        port = ssh_host_cfg.get('port', 22)
        host = ssh_host_cfg.get('hostname', self._original_host)
        LOG.debug("SSH options: host: {}, port: {}".format(
            self._original_host, port,
        ))
        start_command = str(self._cfg.get(
            self._original_host, 'start_command',
            vars={
                'originalhost': self._original_host,
                'host': host,
                'ssh_port': port,
                'hostname': self._original_host.split('.')[0],
                'domain': '.'.join(self._original_host.split('.')[1:]),
            },
        ))

        while True:
            if self._is_reachable(host):
                try:
                    ssh_identification = self._get_ssh_identification(
                        getattr(self, '_host_address', host), port, self._address_family)
                except Exception as err:  # pylint: disable=broad-except
                    LOG.info(err)
                    time.sleep(5)
                    continue

                if self._is_normal_os(ssh_identification):
                    LOG.info(
                        "Normal SSH Server is present. Unlocking seems to be unnecessary. Exiting.")
                    raise SystemExit

                self.run_checkers(NetworkBasedChecker)

                if self._is_preboot(ssh_identification):
                    # Establish connection and let the user deal with potential
                    # host key issues.
                    subprocess.check_call(['ssh', self._original_host, 'true'])

                    init_shell = SimplifiedPxssh(encoding='utf-8', timeout=7)
                    init_shell.login(self._original_host)
                    LOG.info("SSH session to initramfs established.")

                    self.run_checkers(SshBasedChecker, init_shell)

                    LOG.info("All {} checks passed.".format(len(self._checkers)))

                    if not unlock:
                        init_shell.sendline()
                        init_shell.interact()
                        return init_shell.logout()

                    return self.unlock(init_shell)
                else:
                    LOG.info("Waiting for pre-boot environment …")
            else:
                if start_command == 'None':
                    LOG.info("Host offline. Waiting …")
                else:
                    LOG.info("Host offline. Attempting to start using: {}".format(start_command))
                    returncode = subprocess.call(
                        start_command.split(' '),
                        shell=self._cfg.getboolean(self._original_host, 'start_command_shell'),
                    )
                    LOG.info("Start command returned with: {}".format(returncode))
                    start_command = None

            time.sleep(5)

    @staticmethod
    def _get_ssh_identification(host, port, address_family):
        """https://tools.ietf.org/html/rfc4253#section-4.2"""

        inet = socket.AF_INET6
        if address_family in ['any', 'inet']:
            inet = socket.AF_INET
        LOG.debug('Connecting to socket: {}:{}'.format(host, port))
        try:
            with socket.socket(inet, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
                data = sock.recv(255)
        except socket.error:
            raise Exception("SSH server is not responding.")

        return repr(data)

    def _ping(self, host, address_family):
        prog_name = 'fping6'
        if address_family in ['any', 'inet']:
            prog_name = 'fping'

        ping_command = [prog_name, '-A', '-e', '-c', '1', host]
        LOG.debug("Executing ping command: {}".format(' '.join(ping_command)))
        proc = subprocess.Popen(
            ping_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        returncode = proc.wait()
        ping_status = re.split(r'(?:\s+[=:]|,)\s+', proc.stderr.read().decode('utf-8').strip())
        ping_result = proc.stdout.read().decode('utf-8').strip()
        if ping_result:
            LOG.info("Ping result: {}".format(ping_result))

        if returncode == 0 and not hasattr(self, '_host_address'):
            self._host_address = ping_status[0]
            self._ping_rtt_avg = float(ping_status[4].split('/')[1])
            LOG.debug("Set _host_address to {}.".format(self._host_address))
        return returncode

    def _is_reachable(self, host):
        returncode = self._ping(host, self._address_family)
        if returncode == 0:
            return True
        elif returncode == 2:
            raise Exception("{} could not be resolved.".format(host))
        else:
            return False

    @staticmethod
    def _is_preboot(ssh_identification):
        """True if something like SSH-2.0-dropbear_2012.55."""
        return re.search(r'dropbear', ssh_identification, flags=re.IGNORECASE)

    @staticmethod
    def _is_normal_os(ssh_identification):
        """True if something like SSH-2.0-OpenSSH_6.0p1 Debian-4."""
        return re.search(r'openssh', ssh_identification, flags=re.IGNORECASE)

    def run_checkers(self, parent_class, shell=None):
        selected_checkers = [c for c in self._checkers if issubclass(c, parent_class)]
        if not selected_checkers:
            return

        selected_checker_names = [c.__name__ for c in selected_checkers]
        LOG.info("Running {}s: {}".format(
            parent_class.__doc__,
            ', '.join(selected_checker_names)))
        for checker_class in selected_checkers:
            LOG.debug("Running {}.".format(checker_class.__name__))
            checker = checker_class(self)

            violation_message = (
                "{} report an unrecoverable violation causing"
                " FDEunlock to stop at this point.".format(checker_class.__name__))
            if not checker.check(shell=shell):
                if not checker.update():
                    raise CheckViolation(violation_message)
            write_properties_config(self._properties)

    def unlock(self, init_shell):
        """Get passphrase and unlock system."""

        while True:
            init_shell.sendline('cryptroot-unlock')
            # Example: Please unlock disk sda4_crypt (/dev/disk/by-partuuid/3b014afe-1581-11e7-b65d-00163e5e6c0f):
            key_query_pattern = r'Please unlock disk (?P<device_name0>[\w-]+)(?: \((?P<device_name1>[\w/-]+)\)):'
            try:
                cryptroot_unlock_status = init_shell.expect([key_query_pattern, 'not found'])
            except ExceptionPexpect:
                break

            if cryptroot_unlock_status == 1:
                LOG.debug("cryptroot-unlock not present on remote host, copying the version that FDEunlock includes.")
                cryptroot_unlock_file = os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    'data', 'cryptroot-unlock',
                )
                # /usr/bin is also in the $PATH of the initramfs but the dir
                # does not exist by default and I am to lazy to create it :)
                # Also, this might not work for other distros.
                init_shell.copy_to_remote(cryptroot_unlock_file, '/bin/cryptroot-unlock')
                init_shell.sendline('chmod +x /bin/cryptroot-unlock')
                init_shell.prompt()
                continue

            key_query_re = re.match(key_query_pattern, init_shell.after)
            device_names = []
            for device_ind in range(3):
                try:
                    device_name = key_query_re.group('device_name{}'.format(device_ind))
                except IndexError:
                    pass
                else:
                    device_name = device_name.lstrip('/').replace('/', '_')
                    device_names.append(device_name)

            # Bye, bye cryptroot-unlock, we can take it from here.
            init_shell.sendcontrol('c')
            init_shell.prompt()

            key = None
            for device_name in device_names:
                key = self._vault.get_key(self._original_host, device_name)
                if key is not None:
                    break

            if key is None:
                LOG.info("Could not retrieve key for {} (host {}).".format(
                    ', '.join(device_names),
                    self._original_host,
                ))
                key = getpass("Please enter key for {} (or store it in a vault): ".format(
                    ', '.join(device_names),
                )).encode('utf-8')

            LOG.info("Passing key for {} to host {}.".format(
                ', '.join(device_names),
                self._original_host,
            ))
            proc = subprocess.Popen(
                ['ssh', self._original_host, 'cat', '>', '/lib/cryptsetup/passfifo'],
                stdin=subprocess.PIPE,
            )
            proc.communicate(input=key)
            if proc.wait() != 0:
                raise Exception(
                    'Could not pass key for {} to {}.'.format(
                        ', '.join(device_names),
                        self._original_host,
                    )
                )

        try:
            init_shell.logout()
        except ExceptionPexpect:
            pass
        LOG.info("System should be booting now.")
