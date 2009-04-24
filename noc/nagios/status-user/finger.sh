#!/bin/bash

docnagios() {
	echo q | env TERM=ansi LINES=1000 COLS=80 /usr/local/nagios/bin/cnagios -b "$@" | sed 's/\[B/\n/g; s//\n/g' | perl -pe '
s/^.*(?=sipb-nagios)//; # remove garbage at beginning
s/(.)\\[(\d+)b/$1x($2+1)/ge; # (\d+)b means repeat previous character n times
s/\\[(\d+)d//g; # absolute go to line; ignored
s/\\[(\d+)G/" "x($1-$-[0]-1)/ge; # go to absolute horizontal position
s/\\[\d+;(\d+)H/" "x($1-$-[0]-1)/ge; # go to absolute position; line ignored
'
}

read line
case "$line" in
    status*)
	docnagios
	;;
    broken*)
	docnagios -l w
	;;
    *)
	echo "Unknown user"
	;;
esac
#s/\\[\d*[a-zA-Z]//g'
#perl -pe 's/^.*?\[H //s; s/.\[\d+;1H/\n/g; s/^\s+//mg;'

# s/^\s+$//mg; s/Command: .*//s; s/$/\[0m/'
