#!/usr/bin/perl

use strict;
use warnings;
use Sys::Hostname;

sub sendmsg {
    my ($message) = @_;
    open(ZWRITE, "|-", qw|/usr/bin/zwrite -d -c scripts|, '-i', 'root.'.hostname, '-s', hostname) or die "Couldn't open zwrite";
    print ZWRITE $message;
    close(ZWRITE);
}

my $last;

while (my $message = <>) {
    chomp $message;
    $message =~ s/^(.*?): //;
    if ($message =~ m|Accepted (\S+) for (\S+)|) {
	my $send = $message;
	if ($1 eq "gssapi-with-mic") {
	    $send = $last."\n".$send;
	}
	if ($2 eq "root" or $2 eq "logview") {
	    sendmsg($send);
	}
    }
    $last = $message;
}
