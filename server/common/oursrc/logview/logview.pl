#!/usr/bin/perl -T -w

my $elogsrc = '/home/logview/error_log';
# get by uid the caller's name to find the corresponding locker name
my ($caller, $home) = (getpwuid($<))[0, 7];
my $search = "$home/";

print "--- Error logs for $caller ---\n";
open FOO, '<', $elogsrc or die $!;
while (<FOO>) {
    print if index($_, $search) != -1;
}
