# -*- coding: utf-8 -*-

"""
Pre-unlock checkers
"""

from __future__ import absolute_import, division, print_function

import sys
import os
import re
import logging
import subprocess
import time
import hashlib
from random import SystemRandom
from abc import ABC, abstractmethod

#  import secrets

import filecmp
from hexdump import hexdump

__all__ = [
    'LinkLayerAddressChecker',
    'UnauthenticatedLatencyChecker',
    'ChecksumChecker',
    'AuthenticatedLatencyChecker',
]

LOG = logging.getLogger(__name__)


class CheckViolation(Exception):
    pass


def get_default_checkers(_type=object):
    """Return list of default checkers, either the classes or names of the classes."""

    default_checkers = []
    if isinstance(_type, str):
        default_checkers = __all__
    else:
        for default_checker in __all__:
            default_checkers.append(
                getattr(sys.modules[__name__], default_checker))

    return default_checkers


class HostChecker(ABC):
    """Abstract HostChecker class."""

    @abstractmethod
    def check(self, **kwargs):
        """Check host in boot stage."""
        pass

    @abstractmethod
    def update(self, **kwargs):
        """Update check cache while host is in normal operation."""
        pass


class NetworkBasedChecker(HostChecker):  # pylint: disable=abstract-method
    """Network based checker"""
    pass


class SshBasedChecker(HostChecker):  # pylint: disable=abstract-method
    """SSH based checker"""
    pass


class TrustedBootChecker(NetworkBasedChecker):
    """Check trusted boot using remote attestation."""
    def __init__(self):
        raise NotImplementedError("Please implement ;-)")


class TrustedBootVisSshChecker(SshBasedChecker):
    """Check trusted boot by comparing a secret sealed against TPM PCRs values."""
    def __init__(self):
        raise NotImplementedError("Please implement ;-)")


class LinkLayerAddressChecker(NetworkBasedChecker):
    """
    Check network link layer address and compare it to previously observed trusted once.
    """

    def __init__(self, unlocker):

        self._unlocker = unlocker
        self._bin_dir = os.path.join(self._unlocker._data_dir, 'bin')

    def check(self, **kwargs):

        ip_version = '6'
        if self._unlocker._address_family in ['any', 'inet']:
            ip_version = '4'
        ip_command = ['ip', '-' + ip_version, '--oneline', 'neigh', 'show', self._unlocker._host_address]
        proc = subprocess.Popen(
            ip_command,
            stdout=subprocess.PIPE,
            #  stderr=subprocess.PIPE,
        )
        if proc.wait() != 0:
            raise Exception("`ip` command return with non-zero exit code. Command: {}".format(
                ' '.join(ip_command)))

        neigh_status = proc.stdout.read().decode('utf-8').strip().split()
        try:
            link_layer_ind = neigh_status.index('lladdr')
        except ValueError:
            link_layer_ind = -1
            untrusted_link_layer_address = 'Unable to read link layer address'
            LOG.debug(untrusted_link_layer_address)
        else:
            untrusted_link_layer_address = neigh_status[link_layer_ind + 1]
            if not re.match(r"^[0-9a-f]{2}([-:])[0-9a-f]{2}(\1[0-9a-f]{2}){4}$", untrusted_link_layer_address.lower()):
                raise Exception("MAC address not valid: {}.".format(untrusted_link_layer_address))
            LOG.debug("Link layer address: {}".format(untrusted_link_layer_address))

        original_host = self._unlocker._original_host
        link_layer_addresses = self._unlocker._properties.get(original_host, 'link_layer_addresses', fallback='')
        link_layer_addresses = [a.strip() for a in link_layer_addresses.split('\n') if a]

        if len(link_layer_addresses) == 0:
            LOG.info("No link layer addresses found to compare to. Trusting the current once (TOFU).")
            self._unlocker._properties.set(original_host, 'link_layer_addresses', untrusted_link_layer_address)
            return True
        elif untrusted_link_layer_address in link_layer_addresses:
            LOG.info("Link layer address matches the trusted once: {}".format(
                untrusted_link_layer_address))
            return True

        self._link_layer_addresses = link_layer_addresses
        self._untrusted_link_layer_address = untrusted_link_layer_address
        return False

    def update(self):
        """Update check cache while host is in normal operation."""

        LOG.info("Trusted link layer addresses: {}".format(
            ', '.join(self._link_layer_addresses),
        ))
        LOG.info("Current link layer addresses: {}".format(
            self._untrusted_link_layer_address,
        ))
        answer = input("Choose one of 'save', 'ignore' (for current run) or anything else to exit: ")
        if answer == 'save':
            original_host = self._unlocker._original_host
            self._unlocker._properties.set(
                original_host,
                'link_layer_addresses',
                self._untrusted_link_layer_address,
            )
            return True
        elif answer == 'ignore':
            return True
        else:
            return False


class UnauthenticatedLatencyChecker(NetworkBasedChecker):
    """
    Check the unauthenticated latency previously measured by fping if it is within expected boundaries.
    """

    def __init__(self, unlocker):

        self._unlocker = unlocker

    def check(self, **kwargs):

        untrusted_latency = self._unlocker._ping_rtt_avg
        LOG.info("ICMP ping round trip time: {:.4f} ms".format(untrusted_latency))

        original_host = self._unlocker._original_host
        latency = self._unlocker._properties.getfloat(original_host, 'unauthenticated_latency', fallback=-1.0)
        deviation = self._unlocker._cfg.getfloat(original_host, 'unauthenticated_latency_deviation')
        if latency == -1.0:
            LOG.info("No latency found to compare to. Trusting the current one (TOFU).")
            self._unlocker._properties.set(original_host, 'unauthenticated_latency', str(untrusted_latency))
            return True
        elif latency-deviation <= untrusted_latency and untrusted_latency <= latency+deviation:
            LOG.info("Latency is within the boundaries.")
            return True

        self._latency = latency
        self._untrusted_latency = untrusted_latency
        return False

    def update(self):
        LOG.info("Trusted latency: {} ms".format(
            self._latency,
        ))
        LOG.info("Current latency: {} ms".format(
            self._untrusted_latency,
        ))
        answer = input("Choose one of 'save', 'ignore' (for current run) or anything else to exit: ")
        if answer == 'save':
            original_host = self._unlocker._original_host
            self._unlocker._properties.set(
                original_host,
                'unauthenticated_latency',
                str(self._untrusted_latency),
            )
            return True
        elif answer == 'ignore':
            return True
        else:
            return False


class ChecksumChecker(SshBasedChecker):
    """
    Compute checksums for all files in the initramfs and compare the checksums to previously measured trusted once.
    """

    def __init__(self, unlocker):

        self._unlocker = unlocker

        self._bin_dir = os.path.join(self._unlocker._data_dir, 'bin')
        self._checksum_dir = os.path.join(self._unlocker._data_dir, 'checksums')
        os.makedirs(self._bin_dir, exist_ok=True)  # pylint: disable=unexpected-keyword-arg
        os.makedirs(self._checksum_dir, exist_ok=True)  # pylint: disable=unexpected-keyword-arg

        original_host = self._unlocker._original_host
        self._checksum_file = os.path.join(
            self._checksum_dir,
            '{}_initramfs.list'.format(original_host))
        self._untrusted_checksum_file = os.path.join(
            self._checksum_dir,
            '{}_untrusted_initramfs.list'.format(original_host))

    def check(self, shell=None, **kwargs):

        self.checksum_prog = os.path.join(
            self._bin_dir,
            'hashdeep_' + shell.get_platform()
        )
        if os.path.isfile(self.checksum_prog) is False:
            raise IOError("File {} not found.".format(self.checksum_prog))

        shell.copy_to_remote(self.checksum_prog, '/root/hashdeep')
        shell.run_command('chmod 500 /root/hashdeep')

        original_host = self._unlocker._original_host
        additional_checksum_commands = self._unlocker._cfg.get(original_host, 'additional_checksum_commands')
        additional_checksum_commands = [a.strip() for a in additional_checksum_commands.split('\n') if a]

        with open(self._untrusted_checksum_file, 'w') as untrusted_checksum_fh:
            shell.logfile_read = untrusted_checksum_fh
            # Good luck finding a hash collision which works for md5,sha1,sha256
            # plus the length field at the same time ;-)
            # So checksum collisions will probably not be the weakest link here.
            # Not using `-r` of hashdeep because the mangpage of hashdeep warns about it.
            shell.sendline(
                'find / -type f'
                ' -not -path "/proc/*"'
                ' -not -path "/sys/*"'
                ' -not -path "/dev/*"'
                ' -not -path "/run/*"'
                ' -print0'
                #  'find /root -type f -print0'
                #  ' | sort -z'
                ' | xargs -0 /root/hashdeep -r -c md5,sha1,sha256 | grep -v "^[#%]"'
                ' | sort -t "," -k5'
                # Make the path /root-DdbZw2/.ssh/authorized_keys filename deterministic
                #  by replacing it with /root-XXX/.ssh/authorized_keys
                r' | sed "s#,/root-[[:alnum:]]\+/#,/root-XXX/#"'
            )
            shell.prompt()
            for cmd in additional_checksum_commands:
                LOG.info("Running additional command in ChecksumChecker context: {}".format(cmd))
                shell.logfile_read.write('\n# Custom command: ')
                shell.sendline(cmd)
                shell.prompt()
            shell.logfile_read.write('\n')
            shell.logfile_read = None

        # Sanitize input.
        with open(self._untrusted_checksum_file, 'r') as untrusted_checksum_fh:
            with open(self._untrusted_checksum_file + '.tmp', 'w') as untrusted_checksum_tmp_fh:
                untrusted_checksum_tmp_fh.write(
                    re.sub(r'[^\w#/,.:~=*\n|"\' _-]', '', untrusted_checksum_fh.read()))
        os.rename(self._untrusted_checksum_file + '.tmp', self._untrusted_checksum_file)

        if not os.path.isfile(self._checksum_file):
            LOG.info("No checksums found to compare to. Trusting the current once (TOFU).")
            os.rename(self._untrusted_checksum_file, self._checksum_file)
            return True
        elif filecmp.cmp(self._checksum_file, self._untrusted_checksum_file):
            LOG.info("Checksums match the trusted once.")
            return True

        return False

    def update(self):
        LOG.info("Deviation to trusted checksums:")
        original_host = self._unlocker._original_host
        diff_command = self._unlocker._cfg.get(original_host, 'diff_command').split(' ')
        subprocess.call(diff_command + [self._checksum_file, self._untrusted_checksum_file])
        answer = input("Choose one of 'save', 'ignore' (for current run) or anything else to exit: ")
        if LOG.isEnabledFor(logging.DEBUG):
            hexdump(answer.encode('utf-8'))
        if answer.endswith('save'):
            os.rename(self._untrusted_checksum_file, self._checksum_file)
            return True
        elif answer.endswith('ignore'):
            return True
        else:
            return False


class AuthenticatedLatencyChecker(SshBasedChecker):
    """
    Measure the latency over SSH and check if it is within expected boundaries.
    """

    def __init__(self, unlocker):

        self._unlocker = unlocker

    def check(self, shell=None, **kwargs):

        #  token = secrets.token_hex(16)
        token = SystemRandom().getrandbits(64)
        token_hash = hashlib.sha256()
        token_hash.update(str(token).encode('utf-8'))
        token = token_hash.hexdigest()

        start = time.time()
        # A space at the beginning of a command usually ensures it will not end
        # up in the shell history. Does not really matter here, just good practice.
        shell.sendline(' echo "{}"'.format(token))
        shell.expect(token)
        shell.prompt()
        end = time.time()
        untrusted_latency = (end - start) * 1000
        LOG.info("Latency to execute a command over SSH and get the response back: {:.4f} ms".format(untrusted_latency))

        original_host = self._unlocker._original_host
        latency = self._unlocker._properties.getfloat(original_host, 'authenticated_latency', fallback=-1.0)
        deviation = self._unlocker._cfg.getfloat(original_host, 'authenticated_latency_deviation')
        if latency == -1.0:
            LOG.info("No latency found to compare to. Trusting the current one (TOFU).")
            self._unlocker._properties.set(original_host, 'authenticated_latency', str(untrusted_latency))
            return True
        elif latency-deviation <= untrusted_latency and untrusted_latency <= latency+deviation:
            LOG.info("Latency is within the boundaries.")
            return True

        self._latency = latency
        self._untrusted_latency = untrusted_latency
        return False

    def update(self):
        LOG.info("Trusted latency: {} ms".format(
            self._latency,
        ))
        LOG.info("Current latency: {} ms".format(
            self._untrusted_latency,
        ))
        answer = input("Choose one of 'save', 'ignore' (for current run) or anything else to exit: ")
        if answer == 'save':
            original_host = self._unlocker._original_host
            self._unlocker._properties.set(
                original_host,
                'authenticated_latency',
                str(self._untrusted_latency),
            )
            return True
        elif answer == 'ignore':
            return True
        else:
            return False
