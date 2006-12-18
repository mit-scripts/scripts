<?php
require_once('rrdgraph.inc.php');
require_once('rrdgraph.lib.php');

$RRD_IGNORE['ping'][] = 'losspct';

$time = isset($_GET['t'])?rrd_time($_GET['t']):100000;

outputGraph(array('b-m',
		  'o-f',
		  'k-s',
		  's-b',
		  'n-f',
		  'n-b'),
		  'PING', $time, array('legend'=>1,
					'title'=>'%s',
					'geom'=>array(403,146)));
