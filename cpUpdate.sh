#!/usr/bin/env bash
source $HOME/.profile
set -x


if (( $# < 1 )); then
	echo "Usage: $0 <IP> [-r]"
	exit 0
fi

OPT_REUSE=$2
OPT_RUNONLY=$3
LOGFILE=$HOME/cp-build.log
IP=$1
if [[ -z $OPT_REUSE ]]; then
	qmk > ${LOGFILE}
fi

if (( $? != 0 )); then
	exit -1
fi

SOFILES=$(cat ${LOGFILE} | grep "\[LD\] build" | awk '{print $2}')
echo SOFILES=$SOFILES
DIRS=$(for f in $SOFILES; do echo ${f##*rootfs}; done)
DIRS=$(for f in $DIRS; do echo ${f%/*}; done | sort | uniq)
echo $DIRS
CMD='cd /doc/OPERATOR/;'
idx=4
for d in $DIRS; do
	CMD="$CMD mount|grep $d || ./qnx.overlay.sh 32 $d $idx;"
	idx=$(expr $idx + 1)
done

for f in $SOFILES; do
	renamef=`echo $f | sed "s|.*/rootfs\(.*\)/bin/\(.*\)|\1/bin/\2|g"`
	renamef=`echo $renamef | sed "s|.*/rootfs\(.*\)/lib/lib\(.*\)\.so|\1/lib/\2.1|g"`
	CMD="$CMD cp /doc/OPERATOR/${f##*/} ${renamef}; chmod a+x ${renamef};"
done
echo CMD=$CMD
if [[ -z $OPT_RUNONLY ]]; then
	for f in $SOFILES; do
		/opt/lumentum-toolchains/dra821-qnx-R7.1.0_084/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7.1.0-strip $f
		curl -T $f -u OPERATOR:OPERATOR ftp://$IP
	done
fi

$HOME/git/tools/utils.py cp --host $IP run "$CMD"

