#!/usr/bin/env bash

log()
{
    echo "$(basename $0): $@" >> ~/gdb.log
}

if (( $# < 3 )); then
    log "Usage: $0 <IP> <PRG> <gdb.sh> ..."
    exit 1
fi

# log "Launching: $@"
ARGS=""
for i in "$@"; do
    if [[ "$i" =~ ^--.* ]]; then
        ARGS="${ARGS} $i"
    else
        CMD="$i"
    fi
done

read IP PRG GDB <<< "$CMD"
TARGET=/opt/lumentum/bin/$(basename $PRG)
log $GDB $IP $TARGET $PRG $ARGS
exec $GDB -ex "target qnx $IP" -ex "set nto-e $TARGET" -ex "file $PRG" $ARGS
