#!/bin/bash

ulimit -v 102400

read line
line=${line%[:blank:]}
line=${line%}

/sbin/ipvsadm | awk '! ($1 == "->" && $4 == 0 && $5 == 0 && $6 == 0) { print }'
