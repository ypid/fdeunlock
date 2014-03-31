#!/usr/bin/env python
# encoding: utf-8
# This script allows you to unlock encrypted systems via ssh after checking that the initrd has not been tampered with.
# Improved version of https://falkhusemann.de/blog/wp-content/uploads/2013/10/scout.tar.gz (Bash) in Python.
# See http://falkhusemann.de/blog/artikel-veroffentlichungen/tauchfahrt/ for more information.

import pexpect
import logging, sys, re, os
import ping
import subprocess
import time
import filecmp
import socket
from ConfigParser import ConfigParser

# ToDo
# * Read MAC address of target and compare to last time if a MAC address is present for target after ping.

class scout():
    def __init__(self,
            base_config_path = '%s/.scout' % os.environ['HOME'],
            ssh_identity_file = None,
            ssh_known_hosts_file = os.path.join(os.environ['HOME'], '.ssh', 'initrd_known_hosts'),
            shell_promt_regex = '~ # ',
            config_file = '.config.cfg',
            ):
        self._base_config_path = base_config_path

        self._ssh_parms = ssh_parms = '%s -o UserKnownHostsFile=%s' % (
                '-i %s' % ssh_identity_file if ssh_identity_file != None else '',
                ssh_known_hosts_file
                )
        self._hash_check_program = os.path.join(self._base_config_path, 'hashdeep')
        self._shell_promt_regex = re.compile(shell_promt_regex)
        if os.path.isfile(self._hash_check_program) == False:
            raise Exception('File %s not found.' % self._hash_check_program)

        cfg_file = os.path.join(self._base_config_path, config_file)
        cfg_file_permissions = oct(os.stat(cfg_file).st_mode)
        if cfg_file_permissions[-3:] != '600':
            logging.warning('Configuration file (which usually contains passwords) has more file permissions than needed (%s).' % cfg_file_permissions[-4:]
                    + '\n    Please change this by executing the following command: chmod 0600 \'%s\'' % cfg_file)
            sys.exit(20)
        self._cfg = ConfigParser()
        self._cfg.read(cfg_file)

    def _netcat(self, hostname, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, port))
        data = s.recv(50)
        s.close()
        return repr(data)

    def _is_alive(self, hostname):
        return True if os.system('fping -c 2 -q -T5 "%s"' % hostname) == 0 else False

    def _is_preboot(self, ssh_version_string):
        """ True if something like SSH-2.0-dropbear_2012.55. """
        return re.search(r'dropbear', ssh_version_string, flags=re.IGNORECASE)

    def _is_normal_os(self, ssh_version_string):
        """ True if something like SSH-2.0-OpenSSH_6.0p1 Debian-4. """
        return re.search(r'openssh', ssh_version_string, flags=re.IGNORECASE)

    def _unlock_disks(self, hostname, child):
        """ Get password and unlock system. """

        child.sendline('')
        child.expect(self._shell_promt_regex)
        if self._cfg.has_option(hostname, 'password'):
            passwd = self._cfg.get(hostname, 'password')
        else:
            passwd = raw_input('Please enter the unlock password for %s' % hostname)
        child.sendline('echo -n \'%s\' > /lib/cryptsetup/passfifo' % passwd)
        child.expect('exit')
        # child.interact()

    def main(self, hostname, keyfile, port=22):
        self._ssh_parms += ' root@%s' % hostname
        self._hash_file = os.path.join(self._base_config_path, '%s_initrd_hashlist' % hostname)
        self._hash_file_old = '%s.1' % self._hash_file
        while True:
            if self._is_alive(hostname):
                ssh_version_string = self._netcat(hostname, port)
                if self._is_normal_os(ssh_version_string):
                    logging.info('Normal SSH Server is present. Unlocking seems to be not necessary.')
                    sys.exit(1)
                elif not self._is_preboot(ssh_version_string):
                    logging.info('Waiting for pre-boot environment …')
                else: # Dropbear
                    time.sleep(3) # Dropbear needs a bit time to start.
                    logging.info('Preparing pre-boot integrity check …')
                    if os.system('cat %s | ssh %s cat ">" /root/hashdeep' % (
                        os.path.join(self._base_config_path, self._hash_check_program), self._ssh_parms)
                        ) != 0:
                        raise Exception('Could not copy hashdeep over to %s.' % hostname)
                    child = pexpect.spawn('ssh %s' % self._ssh_parms)
                    child.expect(r'BusyBox v1\.20\.2 \(Debian 1:1\.20\.0-7\) built-in shell \(ash\)')
                    child.expect(r"Enter 'help' for a list of built-in commands.")
                    child.expect(self._shell_promt_regex)
                    child.sendline('chmod 500 /root/hashdeep')
                    if os.path.isfile(self._hash_file) == True:
                        os.rename(self._hash_file, self._hash_file_old)
                    else:
                        logging.info('No checksums found to compare to.')
                    child.expect(self._shell_promt_regex)
                    new_hash_file_fh = file(self._hash_file, 'w')
                    child.sendline("/root/hashdeep -r -c sha256 /bin /conf /etc /init /root /sbin /scripts /lib/lib* /lib/klibc* /lib/modules/ /tmp /usr | sed -e '/^#/d' -e '/^%/d'| sort")
                    logging.info('Verifying pre-boot environment …')
                    child.logfile = new_hash_file_fh
                    child.expect(self._shell_promt_regex)
                    child.logfile = None
                    new_hash_file_fh.close()
                    if os.path.isfile(self._hash_file_old) == True and filecmp.cmp(self._hash_file, self._hash_file_old) == False:
                        logging.warning('Changes from last boot checksum detected:')
                        os.system('comm -13 "%s" "%s" | cut -d "," -f 3' % (self._hash_file, self._hash_file_old))
                        if not re.match(r'YES', raw_input('\nDo you want to continue anyway (YES/NO)? ')):
                            sys.exit(1)
                        else:
                            self._unlock_disks(hostname, child)
                    else:
                        self._unlock_disks(hostname, child)
            else:
                logging.info('Host offline. Waiting …')

            time.sleep(5)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG,
        # level=logging.INFO,
        )
    ssh_identity_file = None

    if len(sys.argv) > 1:
        hostname = sys.argv[1]
        if len(sys.argv) > 2:
            ssh_identity_file = sys.argv[2]
    else:
        logging.error('Not enough parameters.'
                + ' 1. Hostname/IP Address.'
                + ' 2. /path/to/dropbear/id_rsa'
                )
        sys.exit(1)

    scout = scout()
    scout.main(hostname, ssh_identity_file)
