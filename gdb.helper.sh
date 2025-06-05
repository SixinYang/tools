#!/usr/bin/env bash
set -x
exec > >(tee $HOME/gdb.detail.log) 2>&1

log()
{
    echo "$(basename $0): $@" >> ~/gdb.log
}

if (( $# < 1 )); then
    log "Usage: $0 <PRJ_ROOTFS> <IP> <PRG> <PID> ..."
    exit 1
fi

log "Launching: $@"

# firstly collect all --opts into $ARGS variable
for i in "$@"; do
    if [[ "$i" =~ ^--.* ]]; then
        ARGS="${ARGS} $i"
    else
        KEYS="${KEYS} $i"
    fi
done

read PRJ_ROOTFS IP PRG PID CMD OTHERS <<< $KEYS
ARGS="${ARGS} $OTHERS"

parse_args(){
	PASSWORD=VaRoomA4
	UTILS="python3 $HOME/bin/utils.py"
	SDK_ROOTFS="/opt/lumentum-toolchains/dra821-qnx-R7.1.0_084/target/qnx7/aarch64le"
	GDB=$(dirname $(realpath $BASH_SOURCE))/gdb.sh
	if [[ "$PRG" == "$SDK_ROOTFS"* ]]; then
		ROOTFS=$SDK_ROOTFS
	else
		ROOTFS=$PRJ_ROOTFS
	fi
	TARGET=${PRG#$ROOTFS}
}

apply_template(){
	sed "s|{{IP}}|$IP|g" $HOME/bin/gdb.helper > $HOME/bin/gdb.helper.apply
	sed -i "s|{{SDK_ROOTFS}}|$SDK_ROOTFS|g" $HOME/bin/gdb.helper.apply
	sed -i "s|{{PRJ_ROOTFS}}|$PRJ_ROOTFS|g" $HOME/bin/gdb.helper.apply
	sed -i "s|{{ROOTFS}}|$ROOTFS|g" $HOME/bin/gdb.helper.apply
	sed -i "s|{{PRG}}|$PRG|g" $HOME/bin/gdb.helper.apply
	sed -i "s|{{TARGET}}|$TARGET|g" $HOME/bin/gdb.helper.apply
}

run(){
	log CMD=$CMD ARGS=$ARGS GDB=$GDB IP=$IP TARGET=$TARGET PROGRAM=$PRG ROOTFS=$ROOTFS PID=$PID SDK_ROOTFS=$SDK_ROOTFS PRJ_ROOTFS=$PRJ_ROOTFS
	cd $ROOTFS
	exec $GDB -ex "target qnx $IP" -ex "set nto-e $TARGET" -ex "file $PRG" $CMD $ARGS
}

