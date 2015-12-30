#!/usr/bin/perl

use Sendmail::Milter;

my %my_milter_callbacks = (
			   'eom' =>        \&my_eom_callback,
			  );

sub find_uid {
  my ($addr, $port) = @_;
  my $file;
  my $search;
  # TODO(quentin): These search strings are probably arch-specific.
  if ($addr eq "::1") {
    $file = "/proc/net/tcp6";
    $search = sprintf("00000000000000000000000001000000:%04X", $port);
  } elsif ($addr eq "127.0.0.1") {
    $file = "/proc/net/tcp";
    $search = sprintf("0100007F:%04X", $port);
  } else {
    return undef;
  }
  my $fh = IO::File->new($file, "r") or die "Cannot read $file: $!";
  <$fh>;  # Eat header
  while (my $line = <$fh>) {
    my @parts = split(" ", $line);
    if ($parts[1] eq $search) {
      return $parts[7];
    }
  }
  return undef;  # Not found.
}

sub my_eom_callback {
  my ($ctx) = @_;

  my $queueid = $ctx->getsymval('i');

  my $addr = $ctx->getsymval('{client_addr}');
  my $port = $ctx->getsymval('{client_port}');

  my $uid = find_uid($addr, $port);

  printf STDERR "Received message from %s:%s (uid %d) (queue ID %s)\n", $addr, $port, $uid, $queueid;

  return SMFIS_ACCEPT;
}

Sendmail::Milter::setconn("local:/var/run/scripts-milter.sock");
Sendmail::Milter::register("scripts",
			   \%my_milter_callbacks, SMFI_CURR_ACTS);

Sendmail::Milter::main();
