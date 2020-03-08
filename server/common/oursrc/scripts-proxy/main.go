package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"strings"

	"inet.af/tcpproxy"
)

var (
	httpAddrs   = flag.String("http_addrs", "0.0.0.0:80", "comma-separated addresses to listen for HTTP traffic on")
	sniAddrs    = flag.String("sni_addrs", "0.0.0.0:443,0.0.0.0:444", "comma-separated addresses to listen for SNI traffic on")
	defaultHost = flag.String("default_host", "scripts.mit.edu", "default host to route traffic to if SNI/Host header cannot be parsed or cannot be found in LDAP")
)

func always(context.Context, string) bool {
	return true
}

type ldapTarget struct {
}

// HandleConn is called by tcpproxy after receiving a connection and sniffing the host.
// If a host could be identified, netConn is an instance of *tcpproxy.Conn.
// If not, it is just an instance of the net.Conn interface.
func (l *ldapTarget) HandleConn(netConn net.Conn) {
	var pool string
	var err error
	if conn, ok := netConn.(*tcpproxy.Conn); ok {
		pool, err = l.resolvePool(conn.HostName)
		if err != nil {
			log.Printf("resolving %q: %v", conn.HostName, err)
		}
	}
	if pool == "" {
		pool, err = l.resolvePool(*defaultHost)
		if err != nil {
			log.Printf("resolving default pool: %v", err)
		}
	}
	if pool == "" {
		netConn.Close()
		return
	}
	laddr := netConn.LocalAddr().(*net.TCPAddr)
	dp := &tcpproxy.DialProxy{
		Addr: fmt.Sprintf("%s:%d", pool, laddr.Port),
		// TODO: Set DialContext to override the source address
	}
	dp.HandleConn(netConn)
}

func (l *ldapTarget) resolvePool(hostname string) (string, error) {
	// TODO: Hardcoding F20 pool until we can resolve the pool.
	return "18.4.86.22", nil
}

func main() {
	flag.Parse()

	var p tcpproxy.Proxy
	t := &ldapTarget{}
	for _, addr := range strings.Split(*httpAddrs, ",") {
		p.AddHTTPHostMatchRoute(addr, always, t)
	}
	for _, addr := range strings.Split(*sniAddrs, ",") {
		p.AddStopACMESearch(addr)
		p.AddSNIMatchRoute(addr, always, t)
	}
	log.Fatal(p.Run())
}
