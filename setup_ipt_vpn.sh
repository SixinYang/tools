#!/usr/bin/env bash

if (( $# < 2 )); then
	echo "Usage: $0 <username> <password>"
	exit 1
fi
USER=$1
PASSWD=$2

# Create new chain
iptables -t nat -N REDSOCKS

# Ignore LANs and some other reserved addresses.
# See http://en.wikipedia.org/wiki/Reserved_IP_addresses#Reserved_IPv4_addresses
# and http://tools.ietf.org/html/rfc5735 for full list of reserved networks.
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 100.64.0.0/10 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 198.18.0.0/15 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -p tcp -m tcp --sport 22 -j RETURN

# Anything else should be redirected to port 12345
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345

# Any tcp connection made by `luser' should be redirected.
#iptables -t nat -A OUTPUT -p tcp -m owner --uid-owner luser -j REDSOCKS

# You can also control that in more precise way using `gid-owner` from
# iptables.
#groupadd socksified
#usermod --append --groups socksified luser
iptables -t nat -A OUTPUT -p tcp -m owner --gid-owner socksified -j REDSOCKS
#iptables -t nat -D OUTPUT -p tcp -j REDSOCKS

# Now you can launch your specific application with GID `socksified` and it
# will be... socksified. See following commands (numbers may vary).
# Note: you may have to relogin to apply `usermod` changes.

#luser$ id
#uid=1000(luser) gid=1000(luser) groups=1000(luser),1001(socksified)
#luser$ sg socksified -c id
#uid=1000(luser) gid=1001(socksified) groups=1000(luser),1001(socksified)
#luser$ sg socksified -c "firefox"

# If you want to configure socksifying router, you should look at
# doc/iptables-packet-flow.png, doc/iptables-packet-flow-ng.png and
# https://en.wikipedia.org/wiki/File:Netfilter-packet-flow.svg
# Note, you should have proper `local_ip' value to get external packets with
# redsocks, default 127.0.0.1 will not go. See iptables(8) manpage regarding
# REDIRECT target for details.
# Depending on your network configuration iptables conf. may be as easy as:
#root# iptables -t nat -A PREROUTING --in-interface eth_int -p tcp -j REDSOCKS


# Setup SOCK5 proxy
#sshpass -p gfarkas ssh -D 1080 -N gfarkas@10.13.166.183
sshpass -p $PASSWD ssh -D 1080 -N ${USER}@Linux64BuildMachine03

