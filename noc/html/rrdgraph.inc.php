<?php
/*
(c)2006 Joe Presbrey <presbrey@mit.edu>
*/

$RRD_PATH = realpath(dirname(__FILE__).'/../ng/rrd');
$RRD_IGNORE['tcp'][] = 'critical_time';
$RRD_IGNORE['tcp'][] = 'warning_time';
$RRD_IGNORE['tcp'][] = 'socket_timeout';
$RRD_IGNORE['users'][] = 'uwarn';
$RRD_IGNORE['users'][] = 'ucrit';
$RRD_IGNORE['mysql'] = $RRD_IGNORE['tcp'];
$RRD_IGNORE['https'] = $RRD_IGNORE['tcp'];
$RRD_IGNORE['disk'][] = 'root';
$RRD_IGNORE['disk'][] = 'user';
$RRD_IGNORE['disk'][] = 'blockpct';
$RRD_IGNORE['disk'][] = 'inodepct';
$RRD_IGNORE['disk'][] = 'inodepct';
$RRD_IGNORE['disk'][] = 'pctfree';
$RRD_IGNORE['disk_/'] = $RRD_IGNORE['disk'];
$RRD_IGNORE['disk_/afs'] = $RRD_IGNORE['disk'];
$RRD_IGNORE['disk_/boot'] = $RRD_IGNORE['disk'];
$RRD_IGNORE['disk_/dev/shm'] = $RRD_IGNORE['disk'];
$RRD_IGNORE['disk_/srv'] = $RRD_IGNORE['disk'];

$RRD_TIMES = array(
	'hour' => 9000,
	'day' => 115200,
	'week' => 691200,
	'month' => 3024000,
	'year' => 34560000);

function rrd_time($var) {
	global $RRD_TIMES;
	if (isset($RRD_TIMES[$var])) {
		$time = $RRD_TIMES[$var];
	} elseif (is_numeric($var)) {
		$time = floor($var);
	} else {
		$time = 115200;
	}
	return $time;
}

?>
