#
# the current cnagios.pl for UW-HEP
#

use strict;

#------------------------------------------------------------------

sub host_plugin_hook {
  local($_) = $_[0];

  s/\(Host assumed to be up\)/assumed up/;
  s/\(Host check timed out\)/timed out/;
  s/\(Not enough data to determine host status yet\)/none/;
  s/\(No Information Returned From Host Check\)/none/;
  s/Ping .*? - (\d+)% packet loss.*/$1% pkt loss/;

  return $_;
}

#------------------------------------------------------------------

sub service_plugin_hook {
  local($_) = $_[0];

  # generic...
  s/Plugin timed out after \d+ seconds/timed out/;

  # check_pingwithperl...
  s/.* (\d+)% packet loss, \d+.\d+ ms ave rtt/$1% pkt loss/;

  # check_tcp...
  s/.* (\d+\.\d+) second[s]? response time.*/$1 sec response/;
  s/.* (\d+) second[s]? response time.*/$1 sec response/;
  s/.* (\d+\.\d+) sec[s]? response time.*/$1 sec response/;

  # check_ftp
  s/.*Invalid response from host/bad response/;

  # chech_ssh...
  s/.* (.*?OpenSSH.*?) .*/$1/;
  s/.*OpenSSH_3.5p1.*/OpenSSH_3.5p1/;
  s/.*Connection refused.*/connection refused/i;

  # check_netsnmp_disk & check_netsnmp_bigdisk...
  # also works for check_dcache_usage...
  while ( $_ =~ /(\d+\.\d+) TB/ ) {
     my $tb = $1;
     # WARNING: will fail for > 9999 GB...
     my $gb = sprintf("%4.4s",int($tb *1024)); 
     $_ =~ s/$tb TB/$gb GB/;
  }
  while ( $_ =~ /(\d+\.\d+) GB/ ) {
     my $gb = $1;
     # WARNING: will fail for > 9999 GB...
     my $gb_new = sprintf("%4.4s",int($gb)); 
     $_ =~ s/$gb GB/$gb_new GB/;
  }
  s/.*?(\d+ GB total,).*?,(\s*\d+ GB avail)/$1$2/;

  # check_netsnmp_loadave...
  s/.* load average: (\d+\.\d+).*/$1 loadave/;

  # check_ntp...
  s/.* Offset ([-]*\d+\.\d+) secs.*/$1 sec offset/;
  s/.* stratum (\d+), offset ([-]*\d+\.\d+).*/stratum $1, $2 sec offset/;
  s/.*Jitter\s+too high.*/jittering/;
  s/.*desynchronized peer server.*/desynchronized peer server/i;
  s/.*probably down.*/down/;

  # check_dhcp et al...
  s/.* Received \d+ DHCPOFFER.*max lease time = (\d+) sec.*/$1 sec lease time/;
  s/.* \d+ in use, (\d+) free/$1 free leases/;
  if ( s/DHCP problem: (.*)/$1/ ) { $_ = lc($_); }

  # check_afs_*...
  s/File Server Performance/Performance/;
  s/.* (\d+ blocked) connections/$1/;
  s/(.*?) AFS (\/.*)/$1 $2/;
  s/(.*?) AFS Volume Quotas/$1 AFS Volumes/;
  s/(\d+) processes running normally/$1 ok processes/;
  s/one process running normally/one ok process/;
  s/% used/%/g;
  s/user.(.*?)/$1/g;
  s/(\d+) volumes under quota/$1 ok volumes/;
  s/db version (\d+.\d+)/db $1/;

  # check_condor_client...
  s/.* vm1 = .*?\/(\S+), vm2 = .*?\/(\S+),.*/$1\/$2/;
  s/.* vm1 = .*?\/(\S+), vm2 = .*?\/(\S+).*/$1\/$2/;
  s/.* cpu = (\S+)/$1/;
  s/CondorQueue.*?(\d+ job[s]?, \d+ running).*/$1/;
  s/.*?No condor status.*/no condor status/;

  # check_condor_pool...
  s/.*?(\d+) nodes.*/$1 nodes/;

  # check_condor_queue...
  s/.*?(\d+ idle, \d+ held)/$1/;

  # check_nsr...
  s/.*?(\d+\.\d+ GB), (\d+ saves) since.*/$1, $2/;
  s/.*?(\d+ GB), (\d+ saves) since.*/$1, $2/;
  s/(\d+ GB avail)able, \d+ GB total/$1/;

  # check_hpjd...
  s/.*? - \(\".*\"\)/printer okay/;
  if ( s/(.*)\s+\(\".*\"\)/$1/ ) { $_ = lc($_); }

  # check_LPRng_queue...
  s/(\d+) active job[s]?/$1 active/;
  s/(\d+) stalled job[s]?/$1 stalled/;
  s/(\d+) spooled job[s]?/$1 spooled/;
  s/(\d+) incoming job[s]?/$1 incoming/;
  s/(\d+) incoming job[s]?/$1 incoming/;

  # check_jug_*...
  s/(\d+) JugRPC processes.*/$1 processes/;
  s/.*JugJobs.*?(\d+) running.*/$1 running/;
  s/.*Jug Storage.*?(\d+) unassigned.*/$1 unassigned/;

  # check_dcache*...
  s/.*no status available.*/not found/;
  s/.*not found in the cellInfo.*/not found/;
  s/service is (.*)/$1/;
  s/.*(\d+) ms ave ping time/$1 ms ping time/;
  s/.*(\d+) ms ping time/$1 ms ping time/;

  # (my) check_traffic & check_ifHighSpeed_traffic...
  # makes columnized XXX.XX Mbps output...
  s/.*? (.*) Traffic/$1 Traffic/;
  s/Internet Traffic/Traffic/;
  if ( $_ =~ /(\d+\.\d+) Gbps in/ ) {
    my $rate = $1;
    my $gbps = sprintf("%6.6s",$rate);
    $_ =~ s/$rate Gbps in/$gbps Gbps in/;
  }
  if ( $_ =~ /(\d+\.\d+) Gbps out/ ) {
    my $rate = $1;
    my $gbps = sprintf("%6.6s",$rate);
    $_ =~ s/$rate Gbps out/$gbps Gbps out/;
  }
  if ( $_ =~ /(\d+\.\d+) Mbps in/ ) {
    my $rate = $1;
    my $mbps = sprintf("%6.6s",$rate);
    $_ =~ s/$rate Mbps in/$mbps Mbps in/;
  }
  if ( $_ =~ /(\d+\.\d+) Mbps out/ ) {
    my $rate = $1;
    my $mbps = sprintf("%6.6s",$rate);
    $_ =~ s/$rate Mbps out/$mbps Mbps out/;
  }
  while ( $_ =~ /(\d+\.\d+) Kbps/ ) {
    my $rate = $1;
    my $mbps = sprintf("%.2f",$rate/1000);
    $mbps = sprintf("%6.6s",$mbps);
    $_ =~ s/$rate Kbps/$mbps Mbps/;
  }
  s/\d+\.\d+ bps/  0.00 Mbps/g;

  # check_airport...
  s/(.*? AirPort) Usage/$1/;
  s/no connected clients/no clients/;
  s/(\d+) connected clients/$1 clients/;

  # check_netsnmp_raid...
  s/.*connect failed.*/connect failed/;
  s/.*degraded.*/degraded/;
  s/.*degraded/degraded/;
  s/.*rebuilding.*/rebuilding/;
  s/.*rebuilding/rebuilding/;
  s/.*built.*/building/;
  s/.*built/building/;
  s/.*optimal.*/optimal/;
  s/.*optimal/optimal/;

  # check_ip_routing_with_mtr
  s/\S+ to \S+ hop not found, first hop out is (\S+)/hop is $1/i;

  # check_phedex
  s/.*(\d+ UP agents).*/$1/;

  # plugin generic...
  s/.*no response.*/connection timed out/i;
  s/.*no route to host.*/no route to host/i;
  s/Socket timeout.*/socket timed out/;

  # nagios generic...
  s/\(Service Check Timed Out\)/check timed out/;
  s/\(No output returned from plugin\)/no output from plugin/;
  s/Service check scheduled for.*/none/;
  s/No data yet.*/no data yet/;
  s/\.$//;

  # generic generic...
  s/.*?OK - //i;
  s/.*?WARNING - //i;
  s/.*?CRITICAL - //i;
  s/.*?UNKNOWN - //i;

  return $_;

}

#------------------------------------------------------------------

# this sub is used for host/service/plugin-output 
# filtering... it should not change...

sub regex_hook {
  my($str,$regex,$mode) = @_;
  if ( $mode == 0 ) { 
    if ( $str =~ /$regex/ ) { return 0 } else { return 1 }
  }
  if ( $mode == 1 ) { 
    if ( $str !~ /$regex/ ) { return 0 } else { return 1 }
  }
  return 2;
}

