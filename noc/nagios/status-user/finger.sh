#!/bin/bash

docnagios() {
	echo q | env TERM=ansi LINES=1000 COLUMNS=80 /usr/local/nagios/bin/cnagios -b "$@" | sed 's/\[B/\n/g; s//\n/g' | perl -pe '
s/^.*(?=sipb-nagios)//; # remove garbage at beginning
s/(.)\\[(\d+)b/$1x($2+1)/ge; # (\d+)b means repeat previous character n times
s/\\[(\d+)d//g; # absolute go to line; ignored
1 while s/\\[(\d+)G/" "x($1-$-[0]-1)/e; # go to absolute horizontal position
1 while s/\\[\d+;(\d+)H/" "x($1-$-[0]-1)/e; # go to absolute position; line ignored
'
}

gethostgroups() {
    cat /etc/nagios3/*.cfg | perl -ne 'print if ( /^(\s*)define hostgroup [\{[]/ ... /[\}\]]/ )' | perl -ne 'm|hostgroup_name\s+(\S+)| and $name = $1; m|members\s+(.+)\s*$| and $members = $1; m|\}| and print "$name\t$members\n"'
}

gethgmembers() {
    gethostgroups | grep "^$1\t" | cut -f 2 -d "	" | sed 's/,/\n/g' | perl -pe 's/\n/|/g' | sed 's/|$//'
}

read line
case "$line" in
    status*)
	docnagios
	;;
    broken*)
	docnagios -l w
	;;
    xvm*)
	docnagios -g "/$(gethgmembers "xvm.*")/"
	;;
    *)
	cat <<EOF
Available information:
finger status@sipb-noc -- all services
finger broken@sipb-noc -- services that are not OKAY
finger xvm@sipb-noc    -- only XVM servers
EOF
      
	;;
esac
#s/\\[\d*[a-zA-Z]//g'
#perl -pe 's/^.*?\[H //s; s/.\[\d+;1H/\n/g; s/^\s+//mg;'

# s/^\s+$//mg; s/Command: .*//s; s/$/\[0m/'
