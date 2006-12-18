<?php
require_once('rrdgraph.inc.php');
require_once('rrdgraph.lib.php');

//$RRD_IGNORE['mysql'][] = 'avg15min';
//$RRD_IGNORE['load'][] = 'avg5min';

$time = isset($_GET['t'])?rrd_time($_GET['t']):100000;

outputGraph(array('k-s',
		  's-b'),
		  'MYSQL', $time, array('legend'=>1,
					'title'=>'%s',
					'geom'=>array(403,146)));
