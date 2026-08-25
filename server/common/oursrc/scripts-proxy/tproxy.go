package main

import (
	"context"
	"log"
	"net"
	"syscall"
)

// TransparentDialer makes a connection to DestAddr using SourceAddr as the non-local source address.
type TransparentDialer struct {
	SourceAddr net.Addr
	DestAddr   net.Addr
}

func (t *TransparentDialer) DialContext(ctx context.Context, network, address string) (net.Conn, error) {
	d := &net.Dialer{
		LocalAddr: t.SourceAddr,
		Control: func(network, address string, c syscall.RawConn) error {
			return c.Control(func(fd uintptr) {
				for _, opt := range []int{
					syscall.IP_TRANSPARENT,
					syscall.IP_FREEBIND,
				} {
					err := syscall.SetsockoptInt(int(fd), syscall.SOL_IP, opt, 1)
					if err != nil {
						log.Printf("control: %s", err)
						return
					}
				}
			})
		},
	}
	return d.DialContext(ctx, network, t.DestAddr.String())
}
