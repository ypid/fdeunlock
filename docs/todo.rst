.. _fdeunlock__ref_todo:

TODO list
=========

.. include:: includes/all.rst

* Better way to retrieve credentials: `Qubes OS`_; https://www.vaultproject.io/
* Isolation using a split-vm approach common in `Qubes OS`_ where the unlocking
  is done in a disposable vm which only gets the keys it needs potentially
  after the remote system has been verified or even in a different vm.
* Support remote attestation (Trusted Computing).
  Ref: http://trousers.sourceforge.net/faq.html#2.1
* Measure time between startup of the server and the availability of the ssh
  service ;) (If possible: If you are like me you also power on your server
  with a shell command ;) )
* Option to run/update validation during normal operation.
* Support key encryption using GnuPG like Mandos_ has implemented it.
  Requires to add user separation to the initramfs because currently FDEunlock
  has full control over target and could just extract the decryption key.
