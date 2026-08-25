package ldap

import (
	"fmt"
	"log"
	"sync"
	"time"

	ldap "gopkg.in/ldap.v3"
)

type conn struct {
	server, baseDn string
	// mu protects conn during reconnect cycles
	// TODO: The ldap package supports multiple in-flight queries;
	// by using a Mutex we are only going to issue one at a
	// time. We should figure out how to do retry/reconnect
	// behavior with parallel queries.
	mu   sync.Mutex
	conn *ldap.Conn
}

func (c *conn) reconnect() {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.conn != nil {
		c.conn.Close()
	}
	var err error
	for {
		log.Printf("connecting to %s", c.server)
		c.conn, err = ldap.Dial("tcp", c.server)
		if err == nil {
			return
		}
		log.Printf("connecting to %s: %v", c.server, err)
		time.Sleep(100 * time.Millisecond)
	}
}

func (c *conn) resolvePool(hostname string) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	escapedHostname := ldap.EscapeFilter(hostname)
	req := &ldap.SearchRequest{
		BaseDN:     c.baseDn,
		Scope:      ldap.ScopeWholeSubtree,
		Filter:     fmt.Sprintf("(|(scriptsVhostName=%s)(scriptsVhostAlias=%s))", escapedHostname, escapedHostname),
		Attributes: []string{"scriptsVhostPoolIPv4"},
	}
	sr, err := c.conn.Search(req)
	if err != nil {
		return "", err
	}
	for _, entry := range sr.Entries {
		return entry.GetAttributeValue("scriptsVhostPoolIPv4"), nil
	}
	// Not found is not an error
	return "", nil
}
