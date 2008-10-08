#!/usr/bin/perl
#
# gitproxy: Wrapper around git daemon for Git virtual hosting.
# version 1.0, released 2008-10-08
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
open2(\*IN, \*OUT, '/usr/local/sbin/ldapize.pl', "git://$host/") or die "$0: open: $!";

# Finally, go into a select loop to transfer the remaining data
# (STDIN -> OUT, IN -> STDOUT), including the client's message to git daemon.
my ($cbuf, $sbuf) = ($msg, '');
my ($rin, $win, $ein) = ('', '', '');
my ($stdout, $out, $stdin, $in) = (fileno(STDOUT), fileno(OUT), fileno(STDIN), fileno(IN));
vec($win, $stdout, 1) = 0;
vec($win, $out, 1) = 1;
vec($rin, $stdin, 1) = 0;
vec($rin, $in, 1) = 1;
while (vec($win, $stdout, 1) or vec($win, $out, 1) or
       vec($rin, $stdin, 1) or vec($rin, $in, 1)) {
    my $n = select(my $rout = $rin, my $wout = $win, my $eout = $ein, undef);
    next if $n < 0 and $! == EINTR;
    $n >= 0 or die "select: $!";
    if (vec($rout, $stdin, 1)) {
	my $n = sysread(STDIN, $cbuf, 4096);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "read: $!";
	vec($rin, $stdin, 1) = 0;
	vec($win, $out, 1) = 1;
    } elsif (vec($rout, $in, 1)) {
	my $n = sysread(IN, $sbuf, 4096);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "read: $!";
	vec($rin, $in, 1) = 0;
	vec($win, $stdout, 1) = 1;
    } elsif (vec($wout, $stdout, 1) && $sbuf ne '') {
	my $n = syswrite(STDOUT, $sbuf);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "write: $!";
	$sbuf = substr($sbuf, $n);
	if ($sbuf eq '') {
	    vec($win, $stdout, 1) = 0;
	    vec($rin, $in, 1) = 1;
	}
    } elsif (vec($wout, $stdout, 1)) {
	vec($win, $stdout, 1) = 0;
	close(STDOUT) or die "close: $!";
	close(IN) or die "close: $!";
    } elsif (vec($wout, $out, 1) && $cbuf ne '') {
	my $n = syswrite(OUT, $cbuf);
	next if $n < 0 and $! == EINTR;
	$n >= 0 or die "write: $!";
	$cbuf = substr($cbuf, $n);
	if ($cbuf eq '') {
	    vec($win, $out, 1) = 0;
	    vec($rin, $stdin, 1) = 1;
	}
    } elsif (vec($wout, $out, 1)) {
	vec($win, $out, 1) = 0;
	close(OUT) or die "close: $!";
	close(STDIN) or die "close: $!";
    }
}
