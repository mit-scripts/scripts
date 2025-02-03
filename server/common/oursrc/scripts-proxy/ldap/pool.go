package ldap

import "log"

// Pool handles a concurrency-safe pool of connections to LDAP servers.
type Pool struct {
	retries int
	// connCh holds open connections to servers.
	connCh chan *conn
}

// NewPool constructs a connection pool that queries for baseDn from servers.
func NewPool(servers []string, baseDn string, retries int) *Pool {
	p := &Pool{
		retries: retries,
		connCh:  make(chan *conn, len(servers)),
	}
	for _, s := range servers {
		c := &conn{
			server: s,
			baseDn: baseDn,
		}
		go p.reconnect(c)
	}
	return p
}

func (p *Pool) reconnect(c *conn) {
	c.reconnect()
	p.connCh <- c
}

// ResolvePool attempts to resolve the pool for hostname to an IP address, returned as a string.
func (p *Pool) ResolvePool(hostname string) (string, error) {
	var ip string
	var err error
	for i := 0; i < p.retries; i++ {
		c := <-p.connCh
		ip, err = c.resolvePool(hostname)
		if err == nil {
			p.connCh <- c
			return ip, err
		}
		log.Printf("resolving %q on %s: %v", hostname, c.server, err)
		go p.reconnect(c)
	}
	return ip, err
}
