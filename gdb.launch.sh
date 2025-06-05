#!/usr/bin/env bash

PWD=$(dirname $(realpath $BASH_SOURCE))
source $PWD/gdb.helper.sh

parse_args
#apply_template
run

