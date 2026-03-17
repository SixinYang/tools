#docker run -it -v /mnt/OttLoadBuild:/sdrive/OttLoadBuild -v /opt/qnx710:/home/root/qnx710 ubuntu-tiqnx:20.04.6 bash

#Issue: need to mount binfmt_misc inside the container, however "docker run -v/proc/sys/fs/binfmt_misc:/proc/sys/fs/binfmt_misc" doesn't work because it is prevented by runc. Also I don't want to run the container via --privileged.
#Workaround: start container firstly, then in another console, use "nsenter" to enter that container and run "mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc"

did=$(docker run -dt -v /mnt/OttLoadBuild:/sdrive/OttLoadBuild -v /opt/qnx710:/home/root/qnx710 ubuntu-tiqnx:20.04.6 bash)
if [ -z $did ]; then
	echo "can't get container ID"
	exit 1
fi
echo "Container: $did"

pid=$(docker top $did|grep bash|awk '{print $2}')
if [ -z $pid ]; then
	echo "can't get PID"
	exit 2
fi
echo "PID=$pid"

sudo nsenter -a -t $pid bash -c "mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc"

docker exec -it $did bash

