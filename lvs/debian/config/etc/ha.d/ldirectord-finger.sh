#!/bin/bash

read line
line=${line%[:blank:]}
line=${line%}

/sbin/ipvsadm
