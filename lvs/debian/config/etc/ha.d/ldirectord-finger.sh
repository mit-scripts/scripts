#!/bin/bash

ulimit -v 10240

read line
line=${line%[:blank:]}
line=${line%}

/sbin/ipvsadm
