#!/usr/bin/env bash

export QNX_TARGET=$HOME/git/devlinux/build/rla1x5/dra821/rootfs
echo $* >> $HOME/bin/gdb.log
echo $1 $2 $3 $4 >> $HOME/bin/gdb.log
#exec /opt/qnx710/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7.1.0-gdb -x $HOME/bin/gdb.init --interpreter=mi2 $1 $2 $3 $4
#exec /opt/qnx710/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7.1.0-gdb -nx --interpreter mi2 $2 $3 $4
exec /opt/lumentum-toolchains/dra821-qnx-R7.1.0_084/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7.1.0-gdb -x $HOME/bin/gdb.init $*
#exec /opt/lumentum-toolchains/dra821-qnx-R7.1.0_084/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7.1.0-gdb $*

