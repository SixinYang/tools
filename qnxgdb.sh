#!/usr/bin/bash
# example: qnxgdb.sh opt/lumentum/bin/aonEfmPro 1327149

echo $# $1 $2 $3

if (( $# < 1 ));then
	echo "Usage: $0 <relative path to program> [pid in target] [sys]"
	exit -1
fi

PRG=$1
PID=$2
SYS=$3
TARGET=${TARGET:-10.89.7.30}

if [ -n "$SYS" ];then
	ROOT=/opt/lumentum-toolchains/dra821-qnx-R7.1.0_084/target/qnx7/aarch64le
	SOLIB=$ROOT/lib:$ROOT/usr/lib
else
	ROOT=build/rla1x5/dra821/debug_files
	#ROOT=build/rla1x5/dra821/rootfs
	SOLIB=$ROOT/opt/lumentum/lib
fi

cd $ROOT/opt/lumentum/lib/
for i in lib*.so;do
	ii=${i#lib}
	it=${ii%.so}.1
	if [ -L $it ];then
		continue
	fi
	ln -s $i $it
done
cd -

source ~/bin/build.vars
if [ -n "$PID" ];then
	vignu gdb $ROOT/$PRG -ex "target qnx $TARGET:8000" -ex "set nto-executable /$PRG" -ex "set solib-search-path $SOLIB" -ex "attach $PID"
else
	vignu gdb $ROOT/$PRG -ex "target qnx $TARGET:8000" -ex "set nto-executable /$PRG" -ex "set solib-search-path $SOLIB"
fi


