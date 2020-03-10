#!/usr/bin/perl

use strict;
use warnings;
use autodie;
use Date::Parse;
use File::Basename;
use Getopt::Long qw(:config bundling);
use IPC::Open2;

chdir dirname($0);

my $now = time();

GetOptions(
  "verbose|v" => \my $verbose,
) or exit 2;

use constant WARNING => 60*60*24*14; # Warn if a cert is expiring within 14 days

my @expired;
foreach my $cert (glob("*.pem"), glob("/var/lib/scripts-certs/*.pem")) {
  open(CERT, "<", $cert);
  my $ins = do {local $/; <CERT>};
  close(CERT);

  for my $in ($ins =~ /^-----BEGIN CERTIFICATE-----\n.*?^-----END CERTIFICATE-----\n/msg) {
    my $pid = open2(\*X509, \*IN, qw(openssl x509 -enddate -noout));
    print IN $in;
    close(IN);
    my $out = do {local $/; <X509>};
    close(X509);
    waitpid($pid, 0);

    my $exp;
    unless (defined $out and ($exp) = $out =~ /^notAfter=(.*)$/m) {
      warn "Cert appears broken: $cert";
      next;
    }

    my $time = str2time($exp);

    if ($verbose || ($time - $now) <= WARNING) {
      push @expired, [$time - $now, $cert, $in];
    }
  }
}

@expired = reverse sort {$a->[0] <=> $b->[0]} @expired;
foreach my $expired_cert (@expired) {
  my ($age, $cert, $in) = @$expired_cert;
  printf "Certificate expiring in %.2f days: %s for ", ($age / (60.0*60*24)), $cert;
  open(IN, '|-', qw(openssl x509 -subject -noout));
  print IN $in;
  close(IN);
}
