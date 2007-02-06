#!/usr/bin/perl -T -w

%ENV = ();
$ENV{'PATH'} = '/bin:/usr/bin';
my $elogsrc = '/home/logview/error_log';
# get by uid the caller's name to find the corresponding locker name
my $caller = (getpwuid $<)[0];
$\ = "\n";

print "--- Error logs for $caller ---";
open FOO, $elogsrc;
my @elogs = <FOO>;
close FOO;
# Prevent deviousness, like web_scripts directories within web_scripts
my @el = grep((m|/([^/]+)/web_scripts/| && $caller eq $1), grep(m|/afs/athena.mit.edu/|, @elogs));
print @el;
