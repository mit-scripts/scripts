#!/bin/sh

# An analog of the Athena athrun utility for scripts.mit.edu.
# The Athena athrun was written by Greg Hudson.
# This version was kludged by Mitchell Berger.
# "athrun moira" runs moira from the moira locker.
# "athrun gnu gls -l" runs gls -l from the gnu locker.

case $# in
0)
  echo "Usage: athrun locker [program] [args ...]" >&2
  exit 1
  ;;
1)
  exec "/mit/$1/bin/$1"
  ;;
*)
  locker=$1
  program=$2
  shift 2;
  exec "/mit/$locker/bin/$program" "$@"
  ;;
esac
