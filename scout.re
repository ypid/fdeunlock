#!/usr/bin/env python
# encoding: utf-8

import pexpect
import logging, sys, re, os
import ping
import subprocess
import time
import filecmp
import socket

class scout():
    def __init__(self,
            base_config_path = '%s/.scout' % os.environ['HOME'],
            ssh_identity_file = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa'),
            ssh_known_hosts_file = os.path.join(os.environ['HOME'], '.ssh', 'initrd_known_hosts'),
            shell_promt_regex = '~ # '
            ):
        self._base_config_path = base_config_path
        self._ssh_parms = ssh_parms = '-i %s -o UserKnownHostsFile=%s' % (ssh_identity_file, ssh_known_hosts_file)
        self._hash_check_program = os.path.join(self._base_config_path, 'hashdeep')
        self._shell_promt_regex = re.compile(shell_promt_regex)
        if os.path.isfile(self._hash_check_program) == False:
            raise Exception('File %s not found.' % self._hash_check_program)

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
                    logging.warning('Waiting for pre-boot environment …')
                else: # Dropbear
                    logging.info('Preparing pre-boot integrity check …')
                    print os.system('cat %s | ssh %s cat ">" /root/hashdeep' % (
                        os.path.join(self._base_config_path, self._hash_check_program), self._ssh_parms)
                        ) == 0
                    child = pexpect.spawn('ssh %s' % self._ssh_parms)
                    child.expect(r'BusyBox v1\.20\.2 \(Debian 1:1\.20\.0-7\) built-in shell \(ash\)')
                    child.expect(r"Enter 'help' for a list of built-in commands.")
                    child.expect(self._shell_promt_regex)
                    child.sendline('chmod 500 /root/hashdeep')
                    if os.path.isfile(self._hash_file) == True:
                        os.rename(self._hash_file, self._hash_file_old)
                    child.expect(self._shell_promt_regex)
                    new_hash_file_fh = file(self._hash_file, 'w')
                    child.sendline("/root/hashdeep -r -c sha256 /bin /conf /etc /init /root /sbin /scripts /lib/lib* /lib/klibc* /lib/modules/ /tmp /usr | sed -e '/^#/d' -e '/^%/d'| sort")
                    print child.logfile
                    logging.info('Verifying pre-boot environment …')
                    child.logfile = new_hash_file_fh
                    child.expect(self._shell_promt_regex)
                    child.logfile = None
                    new_hash_file_fh.close()
                    print filecmp.cmp(self._hash_file, self._hash_file_old)
                    child.interact()

            else:
                logging.warning('Host offline. Waiting …')

            time.sleep(5)


        opt_ssh_parm = ''
        if keyfile != None:
            opt_ssh_parm += '-i "%s"' % keyfile


if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG,
        # level=logging.INFO,
        )
    keyfile = None

    if len(sys.argv) > 1:
        hostname = sys.argv[1]
        if len(sys.argv) > 2:
            keyfile = sys.argv[2]
    else:
        logging.error('Not enough parameters.'
                + ' 1. Hostname/IP Address.'
                + ' 2. /path/to/dropbear/id_rsa'
                )
        sys.exit(1)

    scout = scout()
    scout.main(hostname, keyfile)
