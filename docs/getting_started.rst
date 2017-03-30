Getting started
===============

.. include:: includes/all.rst


Server side setup
-----------------

To check and unlock a FDE server you will need to have that host ready to
accept SSH connections in the initramfs. For this, the Dropbear_ SSH server is recommended.
Refer to :file:`/usr/share/doc/cryptsetup/README.Debian.gz` for details.
In case you use Ansible you might find debops-contrib.dropbear_initramfs_ interesting.

There are also lots of additional resources available on how to set this up:

* Refs: https://blog.tincho.org/posts/Setting_up_my_server:_re-installing_on_an_encripted_LVM/
* https://kiza.eu/journal/entry/697
* http://www.lug-hh.de/wp-content/uploads/kwi_cloudserver_01_fde_0.3.pdf
* https://www.reddit.com/r/linuxadmin/comments/3ot1xk/headless_server_with_fdeluks/

FDEunlock has been successfully tested in the following configurations:

* Debian jessie, dropbear 2014.65-1: IPv4 only, IPv6 only, dual stack
* Debian jessie, dropbear-initramfs 2016.74-2: IPv4 only, IPv6 only, dual stack

Note that you currently might need to set the :ref:`address_family
<fdeunlock__ref_cfg_address_family>` for IPv6 only.

After you setup Dropbear_ you should write down the generated SSH host key
fingerprints over your current, hopefully verified, session. To do this,
issue the following commands and note their output for later comparison:

.. code-block:: shell

   dropbearkey -y -f /etc/dropbear-initramfs/dropbear_rsa_host_key
   dropbearkey -y -f /etc/dropbear-initramfs/dropbear_ecdsa_host_key


Defining a host in FDEunlock
----------------------------

FDEunlock assumes that you can ssh into a host you want to unlock using a
simple :command:`ssh ${host}`.
Any SSH options should be placed into the SSH client configuration. Refer to
the :manpage:`ssh_config(5)` manpage for details.

The following example should get you started:

::

    Host fde-server.example.org-initramfs
        HostName fde-server.example.org
        IdentityFile ~/.ssh/keys/root@fde-server.example.org-initramfs

    Host *-initramfs
        User root
        UserKnownHostsFile ~/.ssh/known_hosts/initramfs
        IdentityFile ~/.ssh/keys/%r@%h
        ## %n would have been perfect instead of %h but this is not supported as of
        ## OpenSSH 7.4? They should have hacked harder.

        ## You might need to allow these for older versions of dropbear:
        # MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,hmac-sha1-96,hmac-sha1
        # KexAlgorithms diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1


Configuration and data location
-------------------------------

FDEunlock follows the `XDG Base Directory Specification`_.
The following places are used by FDEunlock:

``FDEUNLOCK_CONFIG_DIR``
  Used for configuration and keys (FileVault).

``FDEUNLOCK_DATA_DIR``
  Used for data of checkers.

Use the following to figure out where those paths are to be found on your
platform:

.. code-block:: shell

   FDEUNLOCK_CONFIG_DIR="$(python3 -c 'from appdirs import *; print(user_config_dir("fdeunlock"))')"
   FDEUNLOCK_DATA_DIR="$(python3 -c 'from appdirs import *; print(user_data_dir("fdeunlock"))')"


Providing a key using the default FileVault
-------------------------------------------

Place your key (either the passphrase or the keyfile) into
``${FDEUNLOCK_CONFIG_DIR}/keys/${host}_${device_name}.key``. When you use a
passphrase you will need to ensure that no newline is appended to the file (all
common editors appended a newline automatically). One way to avoid the newline
is to run the following command:

.. code-block:: shell

   echo -n 'Please enter your passphrase: '; read -rs pw; echo -n "$pw" > "${key_file}"; unset pw
