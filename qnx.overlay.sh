if (( $# < 1 )); then
	echo $#
	echo "Usage: $0 <size in MBytes> [mount point:default=/opt/lumentum] [device number:default=3]"
	exit 
fi

DEVNUM=${3:-3}
MOUNTPOINT=${2:-/opt/lumentum}
SIZE=${1:-1}

devf-ram -i $DEVNUM -s0,${SIZE}M
waitfor /dev/fs${DEVNUM}p0 5
flashctl -p /dev/fs${DEVNUM}p0 -e -f -n /ram/mount -m
flashctl -p /dev/fs${DEVNUM}p0 -u
flashctl -p /dev/fs${DEVNUM}p0 -m  -n $MOUNTPOINT -vvv
