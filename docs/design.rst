Design principles
-----------------

.. include:: /includes/all.rst

* Standalone. No server running in the background. FDEunlock only runs (and
  hands out keys to servers) when you tell it to do so.

* Easy to setup up.

* The end point/workstation is ultimately* trusted.

  \*There are plans to remove the "ultimately" part. Refer to
  :ref:`fdeunlock__ref_todo`.

* FDEunlock establishes the connection to the host you want to unlock.  Makes
  it easier if your workstation is firewalled, SNATed or is otherwise not
  reachable from the Internet.

* Extensible checker design. Have a good idea for an additional check?
  Great! Just implement the interface of a ``HostChecker`` class and add it to
  the list of default checkers.
