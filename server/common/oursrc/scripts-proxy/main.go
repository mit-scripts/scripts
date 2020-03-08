package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"strings"

	"inet.af/tcpproxy"

	ldap "gopkg.in/ldap.v3"
)

var (
	httpAddrs   = flag.String("http_addrs", "0.0.0.0:80", "comma-separated addresses to listen for HTTP traffic on")
	sniAddrs    = flag.String("sni_addrs", "0.0.0.0:443,0.0.0.0:444", "comma-separated addresses to listen for SNI traffic on")
	ldapServer  = flag.String("ldap_server", "scripts-ldap.mit.edu:389", "LDAP server to query")
	defaultHost = flag.String("default_host", "scripts.mit.edu", "default host to route traffic to if SNI/Host header cannot be parsed or cannot be found in LDAP")
	baseDn      = flag.String("base_dn", "ou=VirtualHosts,dc=scripts,dc=mit,dc=edu", "base DN to query for hosts")
)

func always(context.Context, string) bool {
	return true
}

type ldapTarget struct {
	ldap *ldap.Conn
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
	escapedHostname := ldap.EscapeFilter(hostname)
	req := ldap.NewSearchRequest(
		*baseDn,
		ldap.ScopeWholeSubtree, ldap.NeverDerefAliases, 0, 0, false,
		fmt.Sprintf("(|(scriptsVhostName=%s)(scriptsVhostAlias=%s))", escapedHostname, escapedHostname),
		[]string{"scriptsVhostPoolIPv4"},
		nil,
	)
	sr, err := l.ldap.Search(req)
	if err != nil {
		return "", err
	}
	for _, entry := range sr.Entries {
		return entry.GetAttributeValue("scriptsVhostPoolIPv4"), nil
	}
	// Not found is not an error
	return "", nil
}

func main() {
	flag.Parse()

	l, err := ldap.Dial("tcp", *ldapServer)
	if err != nil {
		log.Fatal(err)
	}
	defer l.Close()

	var p tcpproxy.Proxy
	t := &ldapTarget{ldap: l}
	for _, addr := range strings.Split(*httpAddrs, ",") {
		p.AddHTTPHostMatchRoute(addr, always, t)
	}
	for _, addr := range strings.Split(*sniAddrs, ",") {
		p.AddStopACMESearch(addr)
		p.AddSNIMatchRoute(addr, always, t)
	}
	log.Fatal(p.Run())
}
