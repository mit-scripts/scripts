#!/bin/bash

ulimit -v 102400

# Read and ignore the request
line=foo
while [ -n "$line" ]; do
    read line
    line=${line%[:blank:]}
    line=${line%}
done

# Generate an HTTP reply

echo "HTTP/1.0 200 OK"
echo "Content-type: text/html"
echo ""
echo "<html><head><title>scripts.mit.edu server status</title></head><body><h1>scripts.mit.edu server status</h1><p>The following table shows a list of the servers that are currently handling web requests for scripts.mit.edu:</p><table>"
/sbin/ipvsadm | sed 's/:0//; s/:Port//' | awk 'BEGIN { OFS="</td><td>"; show=1 } /^FWM  2 / { show=1 } /^FWM  [^2] / { show=0 } /->/ { if (show==1) print "<tr><td>" $2, $4, $5, $6 "</td></tr>"}'
echo "</table></body></html>"
