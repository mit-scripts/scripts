<?php
require_once('rrdgraph.inc.php');
require_once('rrdgraph.lib.php');

$RRD_IGNORE['load'][] = 'avg1min';
$RRD_IGNORE['load'][] = 'avg5min';

$time = isset($_GET['t'])?rrd_time($_GET['t']):100000;

outputGraph(array('b-m',
		  'o-f',
		  'k-s',
		  's-b',
		  'n-f',
		  'n-b'),
		  'LOAD', $time, array('legend'=>1,
					'title'=>'%s',
					'geom'=>array(403,146)));
