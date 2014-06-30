#!/bin/bash
# apt-get install fping
if [ -z $1 ]; then
	echo "To unlock with default id_rsa key:"
	echo "	$0 hostname/IP"
	echo "To unlock with custom path to id_rsa key:"
	echo "	$0 hostname/IP /path/to/dropbear/id_rsa"
	exit 1
fi
if [ -z ${2} ]; then
	IDRSA=~/.ssh/id_rsa
fi

HOST="$1"

if [ ! -d ~/.scout ]; then
	mkdir -p ~/.scout
fi

while [ true ]; do
	# Server online?
	fping -q -T5 $HOST > /dev/null 2>&1
	if [ "$?" -eq "0" ]; then
		# Is it a dropbear  from initrd?
		DROPBEAR=`nc -w 1 $HOST 22 | grep -o "[[:print:]]*dropbear[[:print:]]*" | wc -l`
		if [ "${DROPBEAR}" -ne "1" ]; then
			echo -e "\033[1mWaiting for pre-boot environment ...\033[0m"
			sleep 10
			continue
		fi
		echo -e "\033[1mPreparing pre-boot integrity check...\033[0m"
		if ! [ -x ~/.scout/hashdeep ]; then
			echo "hashdeep binary not found in ~/.scout/hashdeep."
			exit 1
		fi
		cat ~/.scout/hashdeep | ssh -i ${IDRSA} -oUserKnownHostsFile=~/.ssh/initrd_known_hosts "root@"${HOST} cat ">" /root/hashdeep
		ssh -qi ${IDRSA} -oUserKnownHostsFile=~/.ssh/initrd_known_hosts "root@"${HOST} "chmod 500 /root/hashdeep"
		if [ -e ~/.scout/${HOST}_initrd_hashlist ]; then
			mv ~/.scout/${HOST}_initrd_hashlist ~/.scout/${HOST}_initrd_hashlist.1

		fi
                echo -e "\033[1mVerifying pre-boot environment...\033[0m"
		ssh -qi ${IDRSA} -t -oUserKnownHostsFile=~/.ssh/initrd_known_hosts "root@"${HOST} "/root/hashdeep -r -c sha256 /bin /conf /etc /init /root /sbin /scripts /lib/lib* /lib/klibc* /lib/modules/ /tmp /usr" | sed -e '/^#/d' -e '/^%/d'| sort > ~/.scout/${HOST}_initrd_hashlist
		ssh -qi ${IDRSA} -oUserKnownHostsFile=~/.ssh/initrd_known_hosts "root@"${HOST} "rm -f /root/hashdeep"
		if [ -e ~/.scout/${HOST}_initrd_hashlist.1 ]; then
			CHANGES=`comm -13 ~/.scout/${HOST}_initrd_hashlist ~/.scout/${HOST}_initrd_hashlist.1  | cut -d "," -f 3 | wc -l`
			if [ "${CHANGES}" -ne "0" ]; then
				echo -e '\E[37;31m'"\033[1mWARNING\033[0m Changes from last boot checksum detected:"
				comm -13 initrd_hashlist initrd_hashlist.old  | cut -d "," -f 3
				echo -e "\nDo you want to continue anyway (y/N)?: "
				read cont
				if ! [ "${cont}t"="yt" ]; then
					exit 1
				fi
			fi
			echo -e '\E[37;30m'"\033[1mChecksums Match\033[0m"
		else
			echo "No checksums found to compare to."
		fi
		ssh -qi ${IDRSA} -t -oUserKnownHostsFile=~/.ssh/initrd_known_hosts "root@"${HOST} 'echo -n `hostname`" unlock Password: ";read -s PASSWORD;echo -n "${PASSWORD}" > /lib/cryptsetup/passfifo'
		echo -e "\n"
		# did it work (no longer a dropbear) or not?
		sleep 5
                DROPBEAR=`nc -w 1 $HOST 22 | grep -o "[[:print:]]*dropbear[[:print:]]*" | wc -l`
		if [ "${DROPBEAR}" -ne "1" ]; then
			echo -e '\E[37;30m'"\033[1mPre-boot environment exited. Unlock ok!\033[0m"
			exit 1
		else
			echo -e '\E[37;31m'"\033[1mWARNING\033[0m Pre-boot environment didn't exit. Wrong password?"
			continue
		fi
	else
		echo "Host offline. Waiting ..."
		sleep 5
	fi
done
