#!/bin/bash

ulimit -v 1024

read line
line=${line%[:blank:]}
line=${line%}

/sbin/ipvsadm
