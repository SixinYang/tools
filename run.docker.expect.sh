#!/usr/bin/bash
if (( $# < 1 )); then
	echo "Usage: $0 <expect file>"
	exit 1
fi

FILE=$1
FULLNAME=$(realpath $FILE)
BASENAME=$(basename $FILE)
USER=tester
docker run -u $USER -it --rm -v ${FULLNAME}:/home/$USER/${BASENAME} -p 162:162/udp -e USERNAME=$USER tester:expect

