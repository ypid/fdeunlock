.. _fdeunlock__ref_host_checkers:

Host checkers
=============

.. include:: includes/all.rst

Before the decryption key gets passed to the remote host, it must be ensured
that the remote host is the authentic one and that it is in a trustworthy state.

Currently, the strongest sign that this is the case is the host key verification
done by SSH which ensures that the remote host has access to it’s private host
key.

Additional to that, a few checkers are implemented which hook in at various
stages of fdeunlock execution.


Network based checkers
----------------------

``LinkLayerAddressChecker``
  Checks the network link layer address as observed by the machine running fdeunlock.
  A link layer address is only expected to be available if the remote machine
  and the machine fdeunlock is running on communicate over the same link layer network.

  This check might be interesting because the link layer address is not stored
  on disk (at least not in clear text). An adversary having only access to the
  disks would have no easy way to get to know this address.

  Note that the link layer address is typically capturable and spoofable in a
  local network.

.. _fdeunlock__ref_UnauthenticatedLatencyChecker:

``UnauthenticatedLatencyChecker``
  Checks the round trip time measured by :command:`fping` based on one ICMP
  packet if it is within expected boundaries.

  The default boundaries is 1.0 ms and can be configured using the
  ``unauthenticated_latency_deviation`` configuration option which is a float
  number representing the time deviation in ms.

  The intention of this check together with the
  :ref:`AuthenticatedLatencyChecker <fdeunlock__ref_AuthenticatedLatencyChecker>`
  is to detect a variant of an `evil maid attack`_ where the host you think you
  are just unlocking is not the one you are actually unlocking.
  Such an attack might have different latency characteristics because even the
  most advanced adversary is still bound by the law of physics.
  For reference, the speed of light is 300 km/ms.


SSH based checkers
------------------

.. _fdeunlock__ref_AuthenticatedLatencyChecker:

``AuthenticatedLatencyChecker``
  Measure the latency over SSH and check if it is within expected boundaries.

  The default boundaries are 10.0 ms and can be configured using the
  ``authenticated_latency_deviation`` configuration option which is a float
  number representing the time deviation in ms.

  Refer to :ref:`UnauthenticatedLatencyChecker
  <fdeunlock__ref_UnauthenticatedLatencyChecker>` for the background.

.. _fdeunlock__ref_ChecksumChecker:

``ChecksumChecker``
  Compute checksums for all files in the initramfs and compare the checksums to
  previously measured trusted once.

  Note that if an reasonably funded adversary is in the position to tamper with
  your initramfs this check will probably not be able to catch them.
  All this check tries to do is to increase the cost of such an attach or even catch less
  skilled attackers.

  There are many ways how this check can be fooled. For example, the check does
  not checksum the loaded/running kernel image nor the boot loader nor the system
  firmware.

  The ``additional_checksum_commands`` configuration option can be used to
  specify additional commands for checksumming/verification. The output of
  those commands is included in the checksum file and compared with the
  previous measurement.
  Multiple commands can be given, separated by newline.
  Example:

  .. code-block:: ini

     [DEFAULT]
     additional_checksum_commands =
       uname -a
       dmesg | egrep '(DMI:|Command line:|Booting paravirtualized kernel on bare hardware)' | sed 's/^\[\s*[[:digit:].]\+\]\s*//;'
       cat /sys/devices/virtual/dmi/id/board_serial /sys/devices/virtual/dmi/id/product_uuid
       ls /dev/disk/by-id/
       dd if=/dev/sda bs=512 count=1 | sha512sum -

  .. You might want to add 2>/dev/zero to dd: Remove race condition between output of sha512sum and dd.

  The ``diff_command`` configuration option can be used to set another text
  diffing program than the default :command:`diff` command.
  Comparison is run on your local machine. Note that the diffing program is
  exposed to untrusted input. The files path to the trusted and the currently
  untrusted checksum file are appended as the last two parameters to the given
  command, in the mentioned order (trusted first; untrusted second/last).
  Example:

  .. code-block:: ini

     [DEFAULT]
     diff_command = git diff --no-index

  Proper remote attestation (Trusted Computing) should be implemented.
  Feel free to add support for this to FDEunlock :-)

  Ref: https://security.stackexchange.com/questions/46548/for-remotely-unlocking-luks-volumes-via-ssh-how-can-i-verify-integrity-before-s
