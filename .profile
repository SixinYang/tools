alias "ll=ls -l"
alias "mk.rla1x5=make JDSU_PRODUCT=rla1x5 TOOLCHAIN=dra821"
alias "mk.ometwin=make JDSU_PRODUCT=ometwin TOOLCHAIN=dra821"

omk(){
        PRODUCT=${1:-ometwin}
	TOOLCHAIN=${2:-dra821}
        make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN clean
        make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN -j16 compile && \
        make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN load
}

dmk(){
	PRODUCT=${1:-ometwin}
	TOOLCHAIN=${2:-dra821}
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh make DEBUG=1 JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN -j16 compile && \
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh make DEBUG=1 JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN load
}

qmk(){
	PRODUCT=${1:-ometwin}
	TOOLCHAIN=${2:-dra821}
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh make DEBUG=1 JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN -j16 compile && \
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh make DEBUG=1 JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN viload
}

vmk(){
	PRODUCT=${1:-ometwin}
	TOOLCHAIN=${2:-dra821}
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh CCFLAGS=-g make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN -j16 compile && \
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh CCFLAGS=-g make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN load
}

vmk_linux(){
	PRODUCT=${1:-grv}
	TOOLCHAIN=${2:-dci-nor}
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/linux/mk_debug.sh CCFLAGS=-g make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN -j16 compile 2>&1 | tee ~/build.log
	JDSU_POSTBUILD=../toolsBuildScripts/target_os/linux/mk_debug.sh CCFLAGS=-g make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN load
}

mkclean(){
	PRODUCT=${1:-grv}
	TOOLCHAIN=${2:-dci-nor}
	make JDSU_PRODUCT=$PRODUCT TOOLCHAIN=$TOOLCHAIN clean
}

#alias "dmk=make DEBUG=1 JDSU_PRODUCT=rla1x5 TOOLCHAIN=dra821 -j16"
#alias "vmk=JDSU_POSTBUILD=../toolsBuildScripts/target_os/qnx/mk_debug.sh CCFLAGS=-g make -j16 JDSU_PRODUCT=rla1x5 TOOLCHAIN=dra821"
export PATH=$PATH:~/bin
export GIT_SSH_COMMAND="ssh -v"
