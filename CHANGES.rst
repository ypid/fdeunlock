Changelog
=========

.. include:: includes/all.rst

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.


`fdeunlock master`_ - unreleased
--------------------------------

.. _fdeunlock master: https://gitlab.com/ypid/fdeunlock/compare/v0.7.1...master

Added
~~~~~

- Mention antievilmaid_, tpmtotp_ and chkboot_ in
  :ref:`fdeunlock__ref_related_projects`. [ypid_]

- Allow to exclude/disable checkers using :ref:`exclude_checkers
  <fdeunlock__ref_config_exclude_checkers>`. [ypid_]

- Make behaviour for UTF-8 decoding errors configurable as :ref:`codec_error_action
  <fdeunlock__ref_config_codec_error_action>`. [ypid_]

Fixed
~~~~~

- Fix support to control ``cryptroot-unlock`` in different configurations. [ypid_]


`fdeunlock v0.7.1`_ - 2017-04-01
--------------------------------

.. _fdeunlock v0.7.1: https://gitlab.com/ypid/fdeunlock/compare/v0.7.0...v0.7.1

Fixed
~~~~~

- FDEunlock tried to execute :command:`None` as command and failed in case the
  ``start_command`` config option was not set.
  Problem was implicit type conversation from ``None`` to ``str``. [ypid_]


fdeunlock v0.7.0 - 2017-03-31
-----------------------------

Added
~~~~~

- Add Python 3 support, documentation, CI, Python package, platform
  independences, unit testing. [ypid_]

- Wrote checkers: ``LinkLayerAddressChecker``, ``UnauthenticatedLatencyChecker``, ``AuthenticatedLatencyChecker``.
  Refer to :ref:`fdeunlock__ref_host_checkers` for details. [ypid_]

- Add configurable :ref:`config_start_command <fdeunlock__ref_config_start_command>`
  for starting an offline machine. [ypid_]

- Add script to PyPI_ under the name `fdeunlock <https://pypi.python.org/pypi/fdeunlock>`__. [ypid_]

- Acquired CII Best Practices badge for FDEunlock. [ypid_]

- Add IPv6 support. [ypid_]

Changed
~~~~~~~

- Major rework and code quality improvements. [ypid_]

- Rename from scout to FDEunlock (project name) and :command:`fdeunlock`
  (package and command name). [ypid_]

- Changed license from GPL-3.0+ to AGPL-3.0. [ypid_]

- Taken over maintenance of the project.
  Refer to `this issue <https://github.com/sdrfnord/scripts/issues/1>`_ for details.
  [ypid_]


scout v0.6.0 - 2016-03-06
-------------------------

Added
~~~~~

- Support interactive mode to drop into a shell after verification. [sdrfnord_]

scout v0.5.0 - 2015-01-13
-------------------------

Changed
~~~~~~~

- Use :manpage:`ssh_config(5)` for ssh options instead custom
  configuration. [sdrfnord_]

- Improved code quality. [sdrfnord_]


scout v0.4.0 - 2014-06-30
-------------------------

Added
~~~~~

- Encryption passphrase can be read from a configuration file. [sdrfnord_]

Changed
~~~~~~~

- Rewrite in Python using pexpect_. [sdrfnord_]


scout.bash v0.1.0 - 2013-10-06
------------------------------

Added
~~~~~

- Initial coding and design in Bash.
  Refer to `Tauchfahrt mit Linux – Colocation Anti-Forensik (German)
  <https://falkhusemann.de/blog/artikel-veroffentlichungen/tauchfahrt/>`_. [husemann_]
