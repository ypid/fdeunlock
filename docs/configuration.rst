Configuration
=============

.. include:: includes/all.rst

Optional configuration can be saved in
:file:`${FDEUNLOCK_CONFIG_DIR}/config.cfg` or in a ``*.cfg`` file below
:file:`${FDEUNLOCK_CONFIG_DIR}/config.d`.

The format is INI as handled by the configparser_ module. Refer to the module’s
documentation for details.

Each host has it’s own section. Supported options inside sections:

.. _fdeunlock__ref_cfg_address_family:

``address_family``
  Specifies which address family to use when connecting.
  Refer to the :manpage:`ssh_config(5)` manpage for details.
  Falls back to your ssh configuration.

.. _fdeunlock__ref_config_start_command:

``start_command``
  Command which is executed to start the remote host in case it is found
  offline.

  The command can make use of the following tokens, which are expanded at
  runtime:

  * ``%(originalhost)s``, hostname as it was specified on the command-line.
  * ``%(host)s``, target hostname, after any substitution by ssh.
  * ``%(ssh_port)s``, SSH port.
  * ``%(hostname)s``, hostname without domain.
  * ``%(domain)s``, domain of the host.

``start_command_shell``
  Boolean determining if :ref:`config_start_command <fdeunlock__ref_config_start_command>`
  is to be executed in the comforting environment of a shell – or not.
  Defaults to ``False``.

:ref:`fdeunlock__ref_host_checkers` might support additional configuration options.
Refer to the :ref:`fdeunlock__ref_host_checkers` section for details.
