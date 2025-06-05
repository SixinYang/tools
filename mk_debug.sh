#!/usr/bin/env bash
# Add this file into build system to make program and libraries compiled just with debug_info compared with normal build.
# Use the following command to make with debug info
# example: output_style=full JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh CCFLAGS=-g make -j16 JDSU_PRODUCT=rla1x5 TOOLCHAIN=dra821 load 2>&1 | tee build.opt-dbg.log

OBJSTRIP=$QNX_HOST/usr/bin/aarch64-unknown-nto-qnx7.1.0-strip
READELF=$QNX_HOST/usr/bin/aarch64-unknown-nto-qnx7.1.0-readelf

name=$1
src=$2
dst=${src%/rootfs/*}/debug_files/${src#*/rootfs/}

# check if the source file is already stripped
$READELF -S $src | grep debug_info
if (( $? != 0 )); then
    echo "$src had been stripped"
    exit 0
fi

# convert lib%.so to %.1
fn=$(basename $dst)
pn=$(dirname $dst)

if [ "${fn#lib}" != "$fn" ];then
    tn=${fn#lib}
    fn=${tn%.so}.1
    dst=$pn/$fn
fi

echo "$0: ($name) $src to $dst"

mkdir -p $(dirname $dst)
cp $src $dst
$OBJSTRIP --strip-debug $src
