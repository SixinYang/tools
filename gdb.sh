#!/usr/bin/env bash

export QNX_TARGET=/opt/lumentum-toolchains/dra821-qnx-R7.1.0_084/target/qnx7
echo "$(basename $0): $@" >> $HOME/gdb.log
exec /opt/lumentum-toolchains/dra821-qnx-R7.1.0_084/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7.1.0-gdb "$@"

