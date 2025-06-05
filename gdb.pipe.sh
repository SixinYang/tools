#!/usr/bin/env bash

PWD=$(dirname $(realpath $BASH_SOURCE))
source $PWD/gdb.helper.sh

parse_args
CFG="--config invalid cp --host ${IP%:*} --telnet_username root --telnet_password $PASSWORD"

if [ "$(basename $CMD)" == "gdb.sh" ]; then
    # transparent call to gdb program
    TARGET=$($UTILS $CFG run "pidin -p $PID arg" | grep -a "$PID /"|awk '{print $2}')
    if [ -z "$TARGET" ]; then
        log "Can't find target command line for $PID"
        exit 1
    fi
    #apply_template
    run
elif [ "$CMD" == "kill" ]; then
    # stop running process via third-party program
    $UTILS $CFG run "$CMD $ARGS"
    exit 0
else
    log "Unknow CMD: $CMD $ARGS"
    exit 1
fi
