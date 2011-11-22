#!/usr/bin/perl

use strict;
use warnings;
use Sys::Hostname;
use Time::HiRes qw(ualarm);
use File::Temp;

our $ZCLASS = "scripts-auto";
our @USERS = qw/root logview/;
my $k5login;
open $k5login, '/root/.k5login';
our @RECIPIENTS = map {chomp; m|([^/@]*)| && $1} <$k5login>;
close $k5login;

our %USERS;
@USERS{@USERS} = undef;

sub zwrite($;$$@) {
    my ($message, $class, $instance, @recipients) = @_;
    $class ||= $ZCLASS;
    $instance ||= 'root.'.hostname;
    open(ZWRITE, "|-", qw|/usr/bin/zwrite -d -n -O log -c|, $class, '-i', $instance, '-s', hostname, @recipients) or die "Couldn't open zwrite";
    print ZWRITE $message;
    close(ZWRITE);
}

my %toclass;

my %sshkeys;

sub buildKeyMap($) {
    my ($file) = @_;
    open (KEYS, $file) or (warn "Couldn't open $file: $!\n" and return);
    while (<KEYS>) {
	chomp;
	my ($fingerprint, $comment) = parseKey($_);
	$sshkeys{$fingerprint} = $comment;
    }
    close(KEYS);
}

sub parseKey($) {
    my ($key) = @_;
    my $tmp = new File::Temp;
    print $tmp $key;
    close $tmp;
    open (KEYGEN, "-|", qw(/usr/bin/ssh-keygen -l -f), $tmp) or die "Couldn't call ssh-keygen: $!";
    my ($line) = <KEYGEN>;
    close(KEYGEN);
    my (undef, $fingerprint, undef) = split(' ', $line, 3);
    my (undef, undef, $comment) = split(' ', $key, 3);
    #print "$fingerprint $comment";
    return ($fingerprint, $comment);
}

buildKeyMap("/root/.ssh/authorized_keys");
buildKeyMap("/root/.ssh/authorized_keys2");

my @message;

while (my $line = <>) {
    @message = $line;
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
	} elsif ($message =~ m|pam_unix\(([^:]+):session\): session \S+ for user (\S+)|) {
	    sendmsg($message) if $1 ne "cron" and exists $USERS{$2};
	} elsif ($message =~ m|^Found matching (\w+) key: (\S+)|) {
	    if ($sshkeys{$2}) {
		sendmsg($message." (".$sshkeys{$2}.")");
	    } else {
		sendmsg($message." (UNKNOWN KEY)");
	    }
	} elsif ($message =~ m|^Out of memory:|) {
	    sendmsg($message);
	} elsif ($message =~ m|^giving \S+ admin rights|) {
	    sendmsg($message);
	} elsif ($message =~ m|^Connection closed|) {
	    # Do nothing
	} elsif ($message =~ m|^Closing connection to |) {
	} elsif ($message =~ m|^Connection from (\S+) port (\S+)|) {
	} elsif ($message =~ m|^Invalid user|) {
	} elsif ($message =~ m|^input_userauth_request: invalid user|) {
	} elsif ($message =~ m|^Received disconnect from|) {
	} elsif ($message =~ m|^Postponed keyboard-interactive|) {
	} elsif ($message =~ m|^Failed keyboard-interactive/pam|) {
	} elsif ($message =~ m|^fatal: Read from socket failed: Connection reset by peer$|) {
	} elsif ($message =~ m|^reverse mapping checking getaddrinfo|) {
	} elsif ($message =~ m|^pam_succeed_if\(sshd\:auth\)\:|) {
	} elsif ($message =~ m|^error: PAM: Authentication failure|) {
	} elsif ($message =~ m|^pam_unix\(sshd:auth\): authentication failure|) {
	} elsif ($message =~ m|^Postponed keyboard-interactive for invalid user |) {
	} elsif ($message =~ m|^Failed keyboard-interactive/pam for invalid user |) {
	} elsif ($message =~ m|^Postponed gssapi-with-mic for |) {
	} elsif ($message =~ m|^Address \S+ maps to \S+, but this does not map back to the address|) {
	} elsif ($message =~ m|^Nasty PTR record .* is set up for .*, ignoring|) {
	} elsif ($message =~ m|^User child is on pid \d+$|) {
	} elsif ($message =~ m|^Transferred: sent \d+, received \d+ bytes$|) {
	} elsif ($message =~ m|^Setting tty modes failed: Invalid argument$|) {
	} elsif ($message =~ m|^ *nrpe .* COMMAND=/etc/nagios/check_ldap_mmr.real$|) {
	} elsif ($message =~ m|^ *root : TTY=|) {
	} elsif ($message =~ m|^Set /proc/self/oom_adj to |) {
	} elsif ($message =~ m|^fatal: mm_request_receive: read: Connection reset by peer$|) {
	} else {
	    sendmsg($message, "scripts-spew");
	}
    }

    foreach my $class (keys %toclass) {
	if ($class eq "scripts-auto") {
	    zwrite($toclass{$class}, $class);
	} else {
	    zwrite($toclass{$class}, $class, undef, @RECIPIENTS);
	}
    }
}
