# scout – Check the integrity of the initrd and mount encrypted root filesystem from remote

This script allows you to unlock encrypted linux systems via ssh after checking that the initrd has not been tampered with.
It is a reimplementation in Python of the bash script script scout.bash which is in the directory scout-bash for reference and further documentation (most of it also applies for this reimplementation).

## List of advantages over the bash implementation

* Does not establish more SSH connections then necessary.
* Improved error handling using pexpect (a certain behavior of the remote shell is expected and tested).
* Much cleaner implemented which allows easier extensibility.
* Encryption password can be read from a configuration password (or from stdin as in the bash version).
* Additional security related features might come in the future (see [todo](#todo)).

## List of disadvantages over the bash implementation

* Has more dependencies on the client system.
* Only tested for one Debian stable system over several months. Might need some
  modification to work with your system (mainly because I am very paranoid and
  the script checks against version numbers of ssh, on [todo list](#todo)).

## ToDo
* Read MAC address of target and compare to last time if a MAC address is present for target after ping.
* Measure time between startup of the server and the availability of the ssh service ;) (If possible: If you are like me you also power on your server with a shell command ;) )
* Add option to run just validation during normal operation.
* Add more configuration options for version numbers of SSH server to make it easier usable for others.
* Write more user documentation.
