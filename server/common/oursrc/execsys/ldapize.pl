#!/usr/bin/perl

use strict;
use warnings;

use Net::LDAP;
use Net::LDAP::Filter;

my $url = $ARGV[0];
my ($proto, $hostname, $path) = $url =~ m|^(.*?)://([^/]*)(.*)| or die "Could not match URL";
my $mesg;

# oh my gosh Net::LDAP::Filter SUCKS
my $filter = bless({and =>
    [{equalityMatch => {attributeDesc  => 'objectClass',
                        assertionValue => 'scriptsVhost'}},
     {or =>
         [{equalityMatch => {attributeDesc  => 'scriptsVhostName',
                             assertionValue => $hostname}},
          {equalityMatch => {attributeDesc  => 'scriptsVhostAlias',
                             assertionValue => $hostname}}]}]},
    'Net::LDAP::Filter');

my $ldap = Net::LDAP->new("ldapi://%2fvar%2frun%2fslapd-scripts.socket/");
$mesg = $ldap->bind();
$mesg->code && die $mesg->error;

$mesg = $ldap->search(base => "ou=VirtualHosts,dc=scripts,dc=mit,dc=edu",
                      filter => $filter);
$mesg->code && die $mesg->error;

my $vhostEntry = $mesg->pop_entry;
my $vhostDirectory = $vhostEntry->get_value('scriptsVhostDirectory');

$mesg = $ldap->search(base => $vhostEntry->get_value('scriptsVhostAccount'),
                      scope => 'base', filter => 'objectClass=posixAccount');
$mesg->code && die $mesg->error;

my $userEntry = $mesg->pop_entry;
my ($homeDirectory, $uidNumber, $gidNumber) =
    map { $userEntry->get_value($_) } qw(homeDirectory uidNumber gidNumber);
(my $scriptsdir = $homeDirectory) =~ s{(?:/Scripts)?$}{/Scripts};

if ($proto eq 'svn') {
  chdir '/usr/libexec/scripts-trusted';
  exec('/usr/sbin/suexec', $uidNumber, $gidNumber, '/usr/libexec/scripts-trusted/svn', "$scriptsdir/svn/$vhostDirectory");
} elsif ($proto eq 'git') {
  chdir '/usr/libexec/scripts-trusted';
  exec('/usr/sbin/suexec', $uidNumber, $gidNumber, '/usr/libexec/scripts-trusted/git', "$scriptsdir/git/$vhostDirectory");
} elsif ($proto eq 'http') {
  print "suexec $uidNumber $gidNumber $scriptsdir/web/$vhostDirectory/$path\n";
} else {
  die "Unknown protocol\n";
}
