#!/bin/bash

ulimit -v 10240

export LINES=1000
export COLUMNS=80
docnagios() {
	echo q | env TERM=ansi /usr/local/nagios/bin/cnagios -b "$@" | sed 's/\[B/\n/g; s//\n/g' | perl -pe '
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
    gethostgroups | grep "^$1	" | cut -f 2 -d "	" | sed 's/,/\n/g' | sort -u | perl -pe 's/\n/|/g' | sed 's/|$//'
}

read line
line=${line%[:blank:]}
line=${line%}

cols=${line##*-}
if [ "$cols" -eq "$cols" ] 2>/dev/null; then
    export COLUMNS="$cols"
    line=${line%-*}
fi
case "$line" in
    status)
	docnagios
	;;
    broken)
	docnagios -l w
	;;
    load)
	docnagios -g /LOAD/
	;;
    scripts-user)
	docnagios -g "/$(gethgmembers "scripts-user.*")/"
	;;
    scripts)
	docnagios -g "/$(gethgmembers "scripts.*")/"
	;;
    xvm)
	docnagios -g "/$(gethgmembers "xvm.*")/"
	;;
    *)
	cat <<EOF
Available information:
finger status@sipb-noc -- all services
finger broken@sipb-noc -- services that are not OKAY
finger load@sipb-noc   -- all LOAD services
finger scripts-user@sipb-noc-- all scripts user services
finger scripts@sipb-noc-- all scripts services
finger xvm@sipb-noc    -- only XVM servers
EOF
	;;
esac
#s/\\[\d*[a-zA-Z]//g'
#perl -pe 's/^.*?\[H //s; s/.\[\d+;1H/\n/g; s/^\s+//mg;'

# s/^\s+$//mg; s/Command: .*//s; s/$/\[0m/'
