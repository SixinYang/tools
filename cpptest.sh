#!/usr/bin/bash

if (( $# < 1 )); then
    echo "Usage: $0 <workspace path> [files/folders to be checked]"
    exit 1
fi

WORKSPACE=$1
FOLDERS=$(git -C $WORKSPACE status -s -uno | awk '{print $2}' | xargs)
FOLDERS="${FOLDERS} $2"

echo """Checking List:
$(echo $FOLDERS | tr " " "\n")
"""

cppcheck --enable=all --inconclusive --xml --xml-version=2 -idevlinux/broadcomLib/ $FOLDERS 2> $WORKSPACE/cppcheck_result.xml
if (( $? != 0 )); then
    echo "cppcheck failed"
    exit 1
fi

cppcheck-htmlreport --file $WORKSPACE/cppcheck_result.xml --report-dir $WORKSPACE/cppcheck_result --source-dir $WORKSPACE
if (( $? != 0 )); then
    echo "cppcheck-htmlreport failed"
    exit 1
fi

echo "Result in folder: $WORKSPACE/cppcheck_result"
echo "Opening result via firefox"

read PID OTHERS <<< $(ps -eo pid,user,cmd | grep $USER |grep deskto[p] | awk '{print $1}')
TGT=$(cat /proc/$PID/environ | tr '\0' '\n'|grep DISPLAY)
if [ -z "$TGT" ]; then
    echo "Can't find DISPLAY"
    return 1
fi

eval "$TGT firefox $WORKSPACE/cppcheck_result/index.html"
