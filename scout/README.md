# scout – Check the integrity of the initrd and mount encrypted root filesystem from remote

This script allows you to unlock encrypted systems via ssh after checking that the initrd has not been tampered with.
It is a reimplementation in Python of the bash script script scout.bash which is under the directory scout-bash for reference and further documentation (most of it also applies for this reimplementation).

## List of advantages over the bash implementation

* Does not open more SSH connections then necessary.
* Improved error handling using pexpect (a certain behavior of the remote shell is expected and tested).
* Much cleaner implemented which allows easier extensibility.
* Encryption password can be read from a configuration password or from stdin.
* Addition security related features might come in the future (see [todo](#todo)).

## List of disadvantages over the bash implementation

* Has more dependencies.
* Only tested for one Debian stable system over several months. Might need some
  modification to work with your system (mainly because I am very paranoid and
  the script checks against version numbers of ssh, needs to be done more
  general or the be configurable).

## ToDo
* Read MAC address of target and compare to last time if a MAC address is present for target after ping.
* Add option to run just validation during normal operation.
