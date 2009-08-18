#!/usr/bin/perl

use File::Basename;
use Date::Parse;

my $dir = dirname($0);
chdir $dir or die "Failed to chdir('$dir'): $!";

my $now = time();

our $verbose = 0;
$verbose = 1 if ($ARGV[0] eq "-v");

use constant WARNING => 60*60*24*14; # Warn if a cert is expiring within 14 days

foreach my $cert (glob "*.pem") {
  open(X509, "-|", qw(openssl x509 -in), $cert, qw(-enddate -noout)) or die "Couldn't invoke openssl x509: $!";
  chomp(my $exp = <X509>);
  close(X509);
  $exp =~ s/^notAfter=// or warn "Cert appears broken: $cert";

  my $time = str2time($exp);

  if ($verbose || ($time - $now) <= WARNING) {
    printf "Certificate expiring in %.2f days: %s for ", (($time - $now) / (60.0*60*24)), $cert;
    system(qw(openssl x509 -in), $cert, qw(-subject -noout));
  }
}
