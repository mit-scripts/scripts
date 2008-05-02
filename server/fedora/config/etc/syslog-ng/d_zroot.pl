#!/usr/bin/perl

use strict;
use warnings;
use Sys::Hostname;
use Time::HiRes qw(ualarm);

our $ZCLASS = "scripts-auto";
our @USERS = qw/root logview/;

our %USERS;
@USERS{@USERS} = undef;

sub zwrite($;$$) {
    my ($message, $class, $instance) = @_;
    $class ||= $ZCLASS;
    $instance ||= 'root.'.hostname;
    open(ZWRITE, "|-", qw|/usr/bin/zwrite -d -O log -c|, $class, '-i', $instance, '-s', hostname) or die "Couldn't open zwrite";
    print ZWRITE $message;
    close(ZWRITE);
}

my %toclass;

while (1) {
    my @message = scalar(<>);
    eval {
        local $SIG{ALRM} = sub { die "alarm\n" }; # NB: \n required
        ualarm(500*1000);
        while (<>) { push @message, $_; }
    };
    chomp @message;
    map { s/^(.*?): // } @message;
    %toclass = ();
    foreach my $message (@message) {
	sub sendmsg ($;$) {
	    my ($message, $class) = @_;
	    $class ||= $ZCLASS;
	    $toclass{$class} .= $message."\n";
	}
	if ($message =~ m|Accepted (\S+) for (\S+)|) {
	    sendmsg($message) if exists $USERS{$2}
	} elsif ($message =~ m|Authorized to (\S+),|) {
	    sendmsg($message) if exists $USERS{$1};
	} elsif ($message =~ m|Root (\S+) shell|) {
	    sendmsg($message);
	} elsif ($message =~ m|session \S+ for user (\S+)|) {
	    sendmsg($message) if exists $USERS{$1};
	} elsif ($message =~ m|^Connection closed|) {
	    # Do nothing
	} elsif ($message =~ m|^Invalid user|) {
	} elsif ($message =~ m|^input_userauth_request: invalid user|) {
	} elsif ($message =~ m|^Received disconnect from|) {
	} elsif ($message =~ m|^fatal: Read from socket failed: Connection reset by peer$|) {
	} elsif ($message =~ m|^reverse mapping checking getaddrinfo|) {
	} elsif ($message =~ m|^pam_succeed_if\(sshd\:auth\)\:|) {
	} elsif ($message =~ m|^Postponed keyboard-interactive for invalid user |) {
	} elsif ($message =~ m|^Failed keyboard-interactive/pam for invalid user |) {
	} elsif ($message =~ m|^Address \S+ maps to \S+, but this does not map back to the address|) {
	} else {
	    sendmsg($message, "scripts-spew");
	}
    }

    foreach my $class (keys %toclass) {
	zwrite($toclass{$class}, $class);
    }
}
