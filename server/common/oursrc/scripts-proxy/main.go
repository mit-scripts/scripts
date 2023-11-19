package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"strings"

	"github.com/mit-scripts/scripts/server/common/oursrc/scripts-proxy/ldap"
	"inet.af/tcpproxy"
)

var (
	httpAddrs   = flag.String("http_addrs", "0.0.0.0:80", "comma-separated addresses to listen for HTTP traffic on")
	sniAddrs    = flag.String("sni_addrs", "0.0.0.0:443,0.0.0.0:444", "comma-separated addresses to listen for SNI traffic on")
	ldapServers = flag.String("ldap_servers", "scripts-ldap.mit.edu:389", "comma-spearated LDAP servers to query")
	defaultHost = flag.String("default_host", "scripts.mit.edu", "default host to route traffic to if SNI/Host header cannot be parsed or cannot be found in LDAP")
	baseDn      = flag.String("base_dn", "ou=VirtualHosts,dc=scripts,dc=mit,dc=edu", "base DN to query for hosts")
	localRange  = flag.String("local_range", "18.4.86.0/24", "IP block for client IP spoofing. If the resolved destination address is in this subnet, the source IP address of the backend connection will be spoofed to match the client IP. This subnet needs to be local to the proxy.")
)

const ldapRetries = 3

func always(context.Context, string) bool {
	return true
}

type ldapTarget struct {
	localPoolRange    *net.IPNet
	ldap              *ldap.Pool
	statuszServer     *HijackedServer
	unavailableServer *HijackedServer
}

// HandleConn is called by tcpproxy after receiving a connection and sniffing the host.
// If a host could be identified, netConn is an instance of *tcpproxy.Conn.
// If not, it is just an instance of the net.Conn interface.
func (l *ldapTarget) HandleConn(netConn net.Conn) {
	var pool string
	var err error
	if conn, ok := netConn.(*tcpproxy.Conn); ok {
		switch conn.HostName {
		case "proxy.scripts.scripts.mit.edu":
			// Special handling for proxy.scripts.scripts.mit.edu
			l.statuszServer.HandleConn(netConn)
			return
		case "heartbeat.scripts.scripts.mit.edu":
			if nolvsPresent() {
				l.unavailableServer.HandleConn(netConn)
				return
			}
		}
		pool, err = l.ldap.ResolvePool(conn.HostName)
		if err != nil {
			log.Printf("resolving %q: %v", conn.HostName, err)
		}
	}
	if pool == "" {
		pool, err = l.ldap.ResolvePool(*defaultHost)
		if err != nil {
			log.Printf("resolving default pool: %v", err)
		}
	}
	// TODO: Forward to sorry server on director?
	if pool == "" {
		l.unavailableServer.HandleConn(netConn)
		return
	}
	laddr := netConn.LocalAddr().(*net.TCPAddr)
	destAddrStr := net.JoinHostPort(pool, fmt.Sprintf("%d", laddr.Port))
	destAddr, err := net.ResolveTCPAddr("tcp", destAddrStr)
	if err != nil {
		netConn.Close()
		log.Printf("parsing pool address %q: %v", pool, err)
		return
	}
	dp := &tcpproxy.DialProxy{
		Addr: destAddrStr,
	}
	if l.localPoolRange.Contains(destAddr.IP) {
		raddr := netConn.RemoteAddr().(*net.TCPAddr)
		td := &TransparentDialer{
			SourceAddr: &net.TCPAddr{
				IP: raddr.IP,
			},
			DestAddr: destAddr,
		}
		dp.DialContext = td.DialContext
	}
	dp.HandleConn(netConn)
}

func main() {
	flag.Parse()

	_, ipnet, err := net.ParseCIDR(*localRange)
	if err != nil {
		log.Fatal(err)
	}

	ldapPool := ldap.NewPool(strings.Split(*ldapServers, ","), *baseDn, ldapRetries)

	var p tcpproxy.Proxy
	t := &ldapTarget{
		localPoolRange:    ipnet,
		ldap:              ldapPool,
		statuszServer:     NewHijackedServer(nil),
		unavailableServer: NewUnavailableServer(),
	}
	for _, addr := range strings.Split(*httpAddrs, ",") {
		p.AddHTTPHostMatchRoute(addr, always, t)
	}
	for _, addr := range strings.Split(*sniAddrs, ",") {
		p.AddStopACMESearch(addr)
		p.AddSNIMatchRoute(addr, always, t)
	}
	log.Fatal(p.Run())
}
