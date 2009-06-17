#!/bin/bash

read line
line=${line%[:blank:]}
line=${line%}

if [ "${line:0:4}" = "GET " ]; then # HTTP request
    echo "Content-type: text/plain"
    echo
    /sbin/ipvsadm
else
    /sbin/ipvsadm
fi
