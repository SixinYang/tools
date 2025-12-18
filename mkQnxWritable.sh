dd if=/dev/zero of=/doc/etc.img bs=1024 count=1024
mkqnx6fs /doc/etc.img
devb-loopback loopback blksz=512,fd=/doc/etc.img
mount /dev/lo0 /doc/mount

