#!/usr/bin/perl
#
# gitproxy: Wrapper around git daemon for Git virtual hosting.
# version 1.1, released 2008-12-28
# Copyright © 2008 Anders Kaseorg <andersk@mit.edu>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

use strict;
use warnings;
use IPC::Open2;
use Errno qw(EINTR);
use IO::Poll qw(POLLIN POLLOUT POLLHUP);

# Receive the first message from the client, and parse out the URL.
my $host;
my $msg = '';
for (;;) {
    my $n = sysread(STDIN, my $buf, 4096);
    next if $n < 0 and $! == EINTR;
    $n >= 0 or die "$0: read: $!";
    $n > 0 or die "$0: unexpected message from client";
    $msg .= $buf;
    my $len;
    if (($len) = $msg =~ m/^([[:xdigit:]]{4})/ and length($msg) >= hex($len)) {
	foreach (split("\0", $')) {
	    last if ($host) = m/^host=(.*)$/;
	}
	last if defined($host);
	die "$0: no host found in client message";
    } elsif ($msg !~ m/^[[:xdigit:]]{0,3}$/) {
	die "$0: unexpected message from client";
    }
}

# Now start the real git daemon based on the URL.
my $pid = open2(\*IN, \*OUT, '/usr/local/sbin/ldapize.pl', "git://$host/") or die "$0: open: $!";

# Finally, go into a poll loop to transfer the remaining data
# (STDIN -> OUT, IN -> STDOUT), including the client's message to git daemon.
my ($cbuf, $sbuf) = ($msg, '');
my $poll = new IO::Poll;
$poll->mask(\*STDOUT => POLLHUP);
$poll->mask(\*OUT => POLLOUT);
$poll->remove(\*STDIN);
$poll->mask(\*IN => POLLIN);
while ($poll->handles()) {
    my $n = $poll->poll();
    next if $n < 0 and $! == EINTR;
    $n >= 0 or die "select: $!";
    if ($poll->events(\*STDIN)) {
	my $n = sysread(STDIN, $cbuf, 4096);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "read: $!";
	$poll->remove(\*STDIN);
	$poll->mask(\*OUT => POLLOUT);
    } elsif ($poll->events(\*IN)) {
	my $n = sysread(IN, $sbuf, 4096);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "read: $!";
	$poll->remove(\*IN);
	$poll->mask(\*STDOUT => POLLOUT);
    } elsif ($poll->events(\*STDOUT) & POLLOUT && $sbuf ne '') {
	my $n = syswrite(STDOUT, $sbuf);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "write: $!";
	$sbuf = substr($sbuf, $n);
	if ($sbuf eq '') {
	    $poll->mask(\*STDOUT => POLLHUP);
	    $poll->mask(\*IN => POLLIN);
	}
    } elsif ($poll->events(\*STDOUT)) {
	$poll->remove(\*STDOUT);
	$poll->remove(\*IN);
	close(STDOUT) or die "close: $!";
	close(IN) or die "close: $!";
    } elsif ($poll->events(\*OUT) & POLLOUT && $cbuf ne '') {
	my $n = syswrite(OUT, $cbuf);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "write: $!";
	$cbuf = substr($cbuf, $n);
	if ($cbuf eq '') {
	    $poll->mask(\*OUT => POLLHUP);
	    $poll->mask(\*STDIN => POLLIN);
	}
    } elsif ($poll->events(\*OUT)) {
	$poll->remove(\*OUT);
	$poll->remove(\*STDIN);
	close(OUT) or die "close: $!";
	close(STDIN) or die "close: $!";
    }
}

while (waitpid($pid, 0) == -1 && $! == EINTR) { }
