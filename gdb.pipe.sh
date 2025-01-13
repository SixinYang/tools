#!/usr/bin/env bash

log()
{
    echo "$(basename $0): $@" >> ~/gdb.log
}

if (( $# < 4 )); then
    log "Usage: $0 <password> <IP> <PID> <cmd...>"
    exit 1
fi

UTILS="python3 $HOME/git/tools/utils.py"
PASSWORD=$1
IP=$2
PID=$3
shift 3

read CMD OTHERS  <<< $*
log INPUT: cmd=$CMD ip=$IP pid=$PID raw="$*"

CFG="--config invalid cp --host ${IP%:*} --telnet_username root --telnet_password $PASSWORD"

if [ "$(basename $CMD)" == "gdb.sh" ]; then
    # transparent call to gdb program
    TARGET=$($UTILS $CFG run "pidin -p $PID arg" | grep -a "$PID /"|awk '{print $2}')
    if [ -z "$TARGET" ]; then
        log "Can't find target command line for $PID"
        exit 1
    fi
    log $* $IP $TARGET
    exec $* -ex "target qnx $IP" -ex "set nto-e $TARGET"
elif [ "$CMD" == "kill" ]; then
    # stop running process via third-party program
    $UTILS $CFG run "$*"
    exit 0
else
    log "Unknow CMD: $*"
    exit 1
fi
