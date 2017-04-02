.. _fdeunlock__ref_related_projects:

Related projects
================

.. include:: includes/all.rst

Mandos_
-------

Mandos has very similar goals as FDEunlock but both address different uses cases.
The key difference is the server/client model. With Mandos you have one or more
Mandos servers providing keys to hosts. The hosts initiate the request for a key.
They find Mandos server either by configured IP address or using Avahi_.

On the other hand, FDEunlock works the other way around. FDEunlock is started
by the user to initiate a connection to the host.
FDEunlock then checks the host and enters the keys it requests which are/where
(previously) provided by the user for that host.

Also, on the implementation side there are a few differences:

+---------------------+----------------------------------------+------------------------------------+
|                     | Mandos_                                | FDEunlock                          |
+=====================+========================================+====================================+
| Transport security  | TLS, GnuTLS, +optional: OpenVPN, …     | SSH, Dropbear_, OpenSSH            |
+---------------------+----------------------------------------+------------------------------------+
| Transport sec certs | OpenPGP keys with GnuTLS               | OpenSSH host keys                  |
+---------------------+----------------------------------------+------------------------------------+
| Mode of operation   | Hosts connect to any Mandos Server     | FDEunlock connects to hosts        |
+---------------------+----------------------------------------+------------------------------------+
| Complexity approx.  | High. Python: ~3500 LOC; C: ~4000      | Medium. Python: ~1000 LOC          |
+---------------------+----------------------------------------+------------------------------------+
| Deployment          | Server daemon                          | Standalone                         |
+---------------------+----------------------------------------+------------------------------------+
| Implemented in      | Server: Python2; Client: C, Bash       | FDEunlock: Python3                 |
+---------------------+----------------------------------------+------------------------------------+
| In Debian_          | `Yes <mandos_debian_packages>`_        | No                                 |
+---------------------+----------------------------------------+------------------------------------+
| Key encrypted       | Yes, only decryptable by target        | No, see :ref:`fdeunlock__ref_todo` |
+---------------------+----------------------------------------+------------------------------------+
| Anti `Evil Maid`_   | Not SOTA_. Dead man switch using ICMP. | Not SOTA_. Multiple checks.        |
+---------------------+----------------------------------------+------------------------------------+
| Development status  | Stable                                 | Beta                               |
+---------------------+----------------------------------------+------------------------------------+
| License             | GPL-3.0+                               | AGPL-3.0                           |
+---------------------+----------------------------------------+------------------------------------+

:Last changed: 2017-03-29

.. _mandos_debian_packages: https://packages.debian.org/search?keywords=mandos

Which to use really depends on your use case.

If you focus on end point/workstation security and don’t put much trust in servers, which
might not always be under your supervision then FDEunlock might work better for
you because that is what it was build for (to use it on workstation of admins).

If you operate a big data center and want to have encrypted servers by default
then Mandos_ should be your number one option.

Note that as both projects use Python to implement similar parts of their
design, using/importing/combining/improving each other is possible but
currently not done.


Plain SSH
---------

If simplicity is key then not much will beat the default way for remote
unlocking as documented by Debian.
Either write the passphrase directly to :file:`/lib/cryptsetup/passfifo` or run
:command:`cryptroot-unlock`.

.. code-block:: shell

   ssh fde-server.example.org-initramfs "echo -ne 'fnord' > /lib/cryptsetup/passfifo"



chkboot_
--------

chkboot is a non-`SOTA`_ Anti `Evil Maid`_ detection tool intended for workstations.
It uses cryptographically strong checksums to measure the content of
:file:`/boot` BUT after the decryption key has already been entered/passed to
the machine.

The functionally is similar to the :ref:`ChecksumChecker <fdeunlock__ref_ChecksumChecker>`
of FDEunlock.


Others?
-------

ypid is not aware of other similar projects. If you are, please get in touch.
