FDEunlock introduction
======================

| |GitLab CI Build Status| (GitLab CI) - |Travis CI Build Status| (Travis CI) - |coverage report| - |Read The Docs| |CII Best Practices|
| |Version| |License| |Python versions| |dev status| |pypi monthly downloads|

FDEunlock – Check and unlock full disk encrypted systems via ssh

This script allows you to unlock full disk encrypted GNU/Linux systems via ssh
after checking that the system has not been tampered with.


Usage example
-------------

Checkout the following example:

::

   fdeunlock --host fde-server.example.org-initramfs
   INFO, 2017-03-29 10:27:41,822: Host offline. Attempting to start using: virsh -c qemu:///system start fde-server
   Domain fde-server started

   INFO, 2017-03-29 10:27:42,726: Start command returned with: 0
   INFO, 2017-03-29 10:27:48,257: Host offline. Waiting …
   INFO, 2017-03-29 10:27:53,264: Ping result: 198.51.100.23 : [0], 84 bytes, 0.51 ms (0.51 avg, 0% loss)
   INFO, 2017-03-29 10:27:53,270: Running Network based checkers: LinkLayerAddressChecker, UnauthenticatedLatencyChecker
   INFO, 2017-03-29 10:27:53,273: Link layer address matches the trusted once.
   INFO, 2017-03-29 10:27:53,283: ICMP ping round trip time: 0.7300 ms
   INFO, 2017-03-29 10:27:53,283: Latency is within the boundaries.
   INFO, 2017-03-29 10:27:54,296: SSH session to initramfs established.
   INFO, 2017-03-29 10:27:54,296: Running SSH based checkers: ChecksumChecker, AuthenticatedLatencyChecker
   INFO, 2017-03-29 10:27:57,487: Checksums match the trusted once.
   INFO, 2017-03-29 10:27:57,559: Latency to execute a command over SSH and get the response back: 71.6000 ms
   INFO, 2017-03-29 10:27:57,560: Trusted latency: 60.256694030762
   INFO, 2017-03-29 10:27:57,560: Current latency: 71.61283493041992
   Choose one of 'save', 'ignore' (for current run) or anything else to exit: save
   INFO, 2017-03-29 10:28:02,739: All 4 checks passed.
   INFO, 2017-03-29 10:28:02,820: Passing key for vda3_crypt to host fde-server.example.org-initramfs.
   INFO, 2017-03-29 10:28:05,140: Could not retrieve key for vdb3_crypt (host fde-server.example.org-initramfs).
   Please enter key for vdb3_crypt (or store it in a vault):
   INFO, 2017-03-29 10:28:28,155: Passing key for vdb3_crypt to host fde-server.example.org-initramfs.
   INFO, 2017-03-29 10:28:43,322: System should be booting now.

The host ``fde-server.example.org-initramfs`` was defined in the ssh
configuration ``~/.ssh/config`` and the key for ``vda3_crypt`` was provided
in
``/home/user/.config/fdeunlock/keys/fde-server.example.org-initramfs_vda3_crypt.key``.
And last but not least, the start command was configured in
``/home/user/.config/fdeunlock/config.cfg``.

Repositories
------------

* `GitLab <https://gitlab.com/ypid/fdeunlock>`_ (primary repo with issue tracker)
* `GitHub <https://github.com/ypid/fdeunlock>`_ (mirror)

Documentation
-------------

* `Read the Docs <https://fdeunlock.readthedocs.io/en/latest/>`_

Authors
-------

* `Marcel McKinnon <https://github.com/sdrfnord>`_
* `Robin Schneider <https://me.ypid.de/>`_

License
-------

`GNU Affero General Public License v3 (AGPL-3.0)`_

.. _GNU Affero General Public License v3 (AGPL-3.0): https://tldrlegal.com/license/gnu-affero-general-public-license-v3-%28agpl-3.0%29
.. _Makefile: https://gitlab.com/ypid/fdeunlock/blob/master/Makefile
.. _tests directory: https://gitlab.com/ypid/fdeunlock/tree/master/tests

.. |GitLab CI Build Status| image:: https://gitlab.com/ypid/fdeunlock/badges/master/build.svg
   :target: https://gitlab.com/ypid/fdeunlock/commits/master

.. |coverage report| image:: https://gitlab.com/ypid/fdeunlock/badges/master/coverage.svg
   :target: https://ypid.gitlab.io/fdeunlock/coverage/

.. |Travis CI Build Status| image:: https://travis-ci.org/ypid/fdeunlock.svg
   :target: https://travis-ci.org/ypid/fdeunlock

.. |Read the Docs| image:: https://readthedocs.org/projects/fdeunlock/badge/?version=latest
   :target: https://fdeunlock.readthedocs.io/en/latest/

.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/829/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/829

.. |Version| image:: https://img.shields.io/pypi/v/fdeunlock.svg
   :target: https://pypi.python.org/pypi/fdeunlock

.. |License| image:: https://img.shields.io/pypi/l/fdeunlock.svg
   :target: https://pypi.python.org/pypi/fdeunlock

.. |Python versions| image:: https://img.shields.io/pypi/pyversions/fdeunlock.svg
   :target: https://pypi.python.org/pypi/fdeunlock

.. |dev status| image:: https://img.shields.io/pypi/status/fdeunlock.svg
   :target: https://pypi.python.org/pypi/fdeunlock

.. |pypi monthly downloads| image:: https://img.shields.io/pypi/dm/fdeunlock.svg
   :target: https://pypi.python.org/pypi/fdeunlock
