Installation
============

.. include:: includes/all.rst


Dependencies
------------

FDEunlock makes use of a few Python and system packages. If you are using
Debian (or a Debian based distribution), you can install them using the package
manager prior to installing FDEunlock:

.. code-block:: shell

   sudo apt install python3-paramiko python3-pexpect python3-appdirs openssh-client fping


Latest release
--------------

You can install FDEunlock by invoking the following commands:

.. code-block:: shell

   gpg --recv-keys 'C505 B5C9 3B0D B3D3 38A1  B600 5FE9 2C12 EE88 E1F0'
   mkdir --parent /tmp/fdeunlock && cd /tmp/fdeunlock
   wget -r -nd -l 1 https://pypi.python.org/pypi/fdeunlock --accept-regex '^https://(test)?pypi\.python\.org/packages/.*\.whl.*'
   current_release="$(find . -type f -name '*.whl' | sort | tail -n 1)"
   gpg --verify "${current_release}.asc" "${current_release}" && pip3 install --upgrade "${current_release}"

Refer to `Verifying PyPI and Conda Packages`_ for more details. Note that this might pull down dependencies in an unauthenticated way! You might want to install the dependencies yourself beforehand.

Or if you feel lazy and agree that `pip/issues/1035 <https://github.com/pypa/pip/issues/1035>`_
should be fixed you can also install FDEunlock like this:

.. code-block:: shell

   pip3 install fdeunlock


Development version
-------------------

If you want to be more on the bleeding edge of FDEunlock development
consider cloning the ``git`` repository and installing from it:

.. code-block:: shell

   gpg --recv-keys 'EF96 BC32 AC57 CFC7 2DF0  1D8C 489A 4D5E C353 C98A'
   git clone --recursive https://gitlab.com/ypid/fdeunlock.git
   cd fdeunlock && git verify-commit HEAD
   echo 'Check if the HEAD commit has a good signature and only proceed in that case!' && read -r fnord
   echo 'Then chose one of the commands below to install FDEunlock and its dependencies:'
   pip3 install --upgrade .
   pip3 install --user --editable .
   ./setup.py develop --user
   ./setup.py install --user
   ./setup.py install


hashdeep for ChecksumChecker
----------------------------

:program:`hashdeep` is used as a statically linked binary for the
:ref:`ChecksumChecker <fdeunlock__ref_ChecksumChecker>`.
You should probably compile it yourself if you want to use the
:ref:`ChecksumChecker <fdeunlock__ref_ChecksumChecker>` using the following
instructions:

.. code-block:: shell

   apt install dpkg-dev
   apt-get build-dep md5deep
   apt-get source md5deep
   cd md5deep-XXX/
   ./configure
   cd src
   editor Makefile
   make
   strip hashdeep

At the editor step you will need to ensure that the :program:`hashdeep` binary
will be statically linked.
Adding ``-static-libgcc`` to the compile options fixed it for ypid.

Then copy the binary to ``${FDEUNLOCK_DATA_DIR}/bin/hashdeep_$(echo "$(uname -s)_$(uname -m)" | tr 'A-Z' 'a-z')``.
Example ``${FDEUNLOCK_DATA_DIR}/bin/hashdeep_linux_x86_64``.
You can run FDEunlock without the binary in place and it will exit with an error
telling you what binary it needed based on the detected platform of your remote system.
