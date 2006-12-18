<?php
/*
(c)2006 Joe Presbrey <presbrey@mit.edu>
inspired by parts of nagiosgraph in Perl
*/

function hashcolor($x) {
  $x .= 'x'; $c=1;
  for($i = 0; $i < strlen($x); $i++) { $c=(51*$c+ord($x{$i}))%216; }
  $h = array(51*floor($c/36), 51*floor($c/6%6), 51*($c%6));
  $i = $n = $m = 0;
  for($i = 0; $i <= 2; $i++) {
    if ($h[$i] < $h[$m]) $m = $i;
    if ($h[$i] > $h[$n]) $n = $i;
  }
  if ($h[$m]>102) $h[$m] = 102;
  if ($h[$n]<153) $h[$n] = 153;
  $n = ($h[2])+($h[1]*256)+$h[0]*256*256;
  $c = sprintf("%06X", ($h[2])+($h[1]*256)+$h[0]*256*256);
  return $c;
}

function findRRD($host, $service) {
	if (isset($GLOBALS['RRD_PATH'])) {
		$rrd = $GLOBALS['RRD_PATH'];
	} else {
		$rrd = dirname(__FILE__);
	}
	$f = glob("$rrd/{$host}_{$service}_*.rrd");
	if (count($f)) {
		$o = array_shift($f);
	} else {
		$host = str_replace('-','%2D',rawurlencode($host));
		$service = str_replace('-','%2D',rawurlencode($service));
		$f = glob("$rrd/{$host}_{$service}_*.rrd");
		if (count($f)) {
			$o = array_shift($f);
		} else {
			$f = glob("$rrd/{$host}_{$service}*.rrd");
			if (count($f))
				$o = array_shift($f);
		}
	}
	$p = realpath($o);
	if (strlen($p)>strlen($host)+strlen($service)) {
		if (preg_match_all('/([^_]+)_([^_]+)_(.+).rrd/iU', basename($p), $m)) {
			return array($p, $m[1][0], $m[2][0], $m[3][0]);
		}
	}
}

function graphInfo($file) {
	$rrdinfo = `rrdtool info $file`;
	preg_match_all('/ds\[([^\]]*)\]\./',$rrdinfo,$ds);
	$lines = array_unique($ds[1]);
	//sort($lines);
	return $lines;
}

function makeDefs($file, $ignores=array(), $oneHost=true) {
	$info = graphInfo($file[0]);
	$defs = array();
	$def = 'DEF:$dj=$file:$di:AVERAGE' .
               ' LINE2:$dj#$c:$dj' .
               ' GPRINT:$dj:MAX:Max\\\\:\\ %6.2lf%s' .
               ' GPRINT:$dj:AVERAGE:Avg\\\\:\\ %6.2lf%s' .
               ' GPRINT:$dj:MIN:Min\\\\:\\ %6.2lf%s' .
               ' GPRINT:$dj:LAST:Cur\\\\:\\ %6.2lf%s\\\\n';
	foreach($info as $sv) {
		if (in_array(strtolower($sv), $ignores)) continue;
		$d = str_replace('$di',$sv,$def);
		if ($oneHost) {
			$d = str_replace('$dj',$sv,$d);
			$d = str_replace('$c',hashcolor($sv),$d);
		} else {
			$d = str_replace('$dj',urldecode($file[1]).'_'.$sv,$d);
			$d = str_replace('$c',hashcolor(md5($file[0].$sv)),$d);
		}
		$d = str_replace('$file',$file[0],$d);
		$defs[] = $d;
	}
	return implode(' ',$defs);
}

function outputGraph($hosts, $service, $time, $opts = array()) {
	if (!is_array($hosts)) $hosts = array($hosts);
	$oneHost = count($hosts)<=1;
//	if (!is_array($services)) $services = array($services);
	$defs = array();
	$args = array();
	$files = array();
	foreach($hosts as $host) {
		$file = findRRD($host, $service);
		if (is_array($file) && strlen($file[0])) $files[] = $file;
	}
	foreach($files as $file) {
		if (isset($GLOBALS['RRD_IGNORE'])
		   && isset($GLOBALS['RRD_IGNORE'][strtolower($service)])) {
			$def = makeDefs($file, $GLOBALS['RRD_IGNORE'][strtolower($service)], $oneHost);
		} else {
			$def = makeDefs($file, array(), $oneHost);
		}
		if (strlen($def)) $defs[] = $def;
	}

	if (count($opts))
		extract($opts);
	if (isset($geom)) {
		if (isset($geom[0]))
			$args[] = '-w '.$geom[0];
		if (isset($geom[1]))
			$args[] = '-h '.$geom[1];
	}
	if (isset($legend) && !$legend) {
		$args[] = '-g';
	}
	if (isset($title)) {
		if (count($files)) {
			list($fhost, $fservice, $fdb) = array_slice(explode('_',basename($files[0][0])),0,3);
			if ($oneHost) {
				$title = str_replace('%h', urldecode($fhost), $title);
				$title = str_replace('%s', urldecode($fservice), $title);
			} else {
				$title = str_replace('%h', implode(',',$hosts), $title);
				$title = str_replace('%s', urldecode($service), $title);
			}
		}
		$title = escapeshellarg($title);
		if (strlen($title)) $args[] = "-v$title";
	}

	if (count($defs)) {
		$defs = implode(' ', $defs);
		if (count($args))
			$argstr = implode(' ', $args);
		$cmd = "rrdtool graph - -a PNG --start -$time $defs $argstr";
		$data = `$cmd`;
		if (strlen($data)>0) {
			header('Content-Type: image/png');
			echo $data;
			exit;
		} else {
			echo "failed: $cmd";
		}
	}
}

//outputGraph('better-mousetrap', 'DISK: /', 192000);
