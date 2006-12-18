<?php
/*
(c)2006 Joe Presbrey <presbrey@mit.edu>
*/

include('rrdgraph.inc.php');
require_once('rrdgraph.lib.php');

if (isset($_GET['h'])&&isset($_GET['s'])&&isset($_GET['i'])) {
	displayGraph($_GET['h'],$_GET['s'],$_GET['i']);
	exit;
}

$skip_host[] = 'localhost';
$skip_service[] = 'DISK_%2Fafs';
$skip_service[] = 'DISK_%2Fboot';
$skip_service[] = 'DISK_%2Fdev%2Fshm';
$only_host = array();
if (isset($_GET['host']))
	$only_host[] = $_GET['host'];
$only_service = array();
if (isset($_GET['service']))
	$only_service[] = $_GET['service'];

function getServices($time=115200) {
	$s = array();
	foreach(glob("{$GLOBALS['RRD_PATH']}/*.rrd") as $f) {
		if (time()-filemtime($f)<=$time) {
			$e = explode('_', basename($f));
//			//$s[$e[0]][] = $e[1];
			if ($e[1] == 'DISK')
				$s[array_shift($e)][] = substr(implode('_', $e),0,-4);
			else {
//				array_pop($e);
				$s[$e[0]][] = $e[1];
			}
		}
	}
	return $s;
}

function displayGraph($host,$service,$time=null) {
	$times = array(
		'hour' => 19200,
		'day' => 115200,
		'week' => 691200,
		'month' => 3024000,
		'year' => 34560000);
	$geom = array(
		'hour' => '450x180',
		'day' => '300x100',
		'week' => '300x100',
		'month' => '300x100',
		'year' => '300x100');
	$title = array(
		'hour' => "$host: $service",
		'day' => "$service today",
		'week' => "$service this week",
		'month' => "$service this month",
		'year' => "$service this year");
	if (is_null($time) || !isset($times[$time])) $time = 'day';
	outputGraph($host, $service, $times[$time], array('legend'=>($time!='hour'?false:true),
							'title'=>$title[$time],
							'geom'=>explode('x',$geom[$time])));
	//virtual('/ng/cgi-bin/show.cgi?host='.$host.'&service='.$service.'&graph='.$times[$time].'&geom='.$geom[$time].'&rrdopts='.str_replace(' ','_',$rrdopts[$time]));
	//virtual('/ng/cgi-rin/show.cgi?host='.$host.'&service='.$service.'&graph=118800');
	//virtual('/ng/cgi-bin/show.cgi?host=better-mousetrap&service=LOAD&db=load&graph=118800');
	exit;
}

//displayGraph('better-mousetrap','LOAD');
echo '<table border=0 cellspacing=0 cellpadding=0>';
foreach(getServices() as $host=>$services) {
	$host = urldecode($host);
	if (in_array($host, $skip_host)) continue;
	if (count($only_host) && !in_array($host, $only_host)) continue;
	echo '<tr>';
	foreach($services as $service) {
		if (in_array($service, $skip_service)) continue;
		if (count($only_service) && !in_array($service, $only_service)) continue;
		echo '<td>';	
		printf('<img src="show.php?h=%s&s=%s&i=%s">', $host, $service, 'hour');
		echo '</td><td>';
		printf('<img src="?h=%s&s=%s&i=%s">', $host, $service, 'day');
		echo '<br />';
		printf('<img src="?h=%s&s=%s&i=%s">', $host, $service, 'week');
		echo '</td>';
	}
	echo '</tr>';
}
echo '</table>';
