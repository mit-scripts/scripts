package main

import (
	"errors"
	"net"
	"net/http"
	_ "net/http/pprof"
	"os"
)

func nolvsPresent() bool {
	if _, err := os.Stat("/etc/nolvs"); err == nil {
		return true
	}
	return false
}

// HijackedServer is an HTTP server that serves from connections hijacked from another server instead of a listening socket.
// (See net/http.Hijacker for the opposite direction.)
// Users can call HandleConn to handle any request(s) waiting on that net.Conn.
type HijackedServer struct {
	connCh chan net.Conn
}

// NewHijackedServer constructs a HijackedServer that handles incoming HTTP connections with handler.
func NewHijackedServer(handler http.Handler) *HijackedServer {
	s := &HijackedServer{
		connCh: make(chan net.Conn),
	}
	go http.Serve(s, handler)
	return s
}

// Accept is called by http.Server to acquire a new connection.
func (s *HijackedServer) Accept() (net.Conn, error) {
	c, ok := <-s.connCh
	if ok {
		return c, nil
	}
	return nil, errors.New("closed")
}

// Close shuts down the server.
func (s *HijackedServer) Close() error {
	close(s.connCh)
	return nil
}

// Addr must be present to implement net.Listener
func (s *HijackedServer) Addr() net.Addr {
	return nil
}

// HandleConn instructs the server to take control of c and handle any HTTP request(s) that are waiting.
func (s *HijackedServer) HandleConn(c net.Conn) {
	s.connCh <- c
}

// NewUnavailableServer constructs a HijackedServer that serves 500 Service Unavailable for all requests.
func NewUnavailableServer() *HijackedServer {
	return NewHijackedServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "0 proxy nolvs", http.StatusServiceUnavailable)
	}))
}
