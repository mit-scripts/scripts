<?php
include('rrdgraph.inc.php');
require_once('rrdgraph.lib.php');

import_request_variables('g','i_');

$host = isset($i_host)?$i_host:'better-mousetrap';
$service = isset($i_service)?$i_service:'LOAD';
$time = isset($i_time)?$i_time:'115200';
$legend = isset($i_legend)&&$i_legend==0?0:1;
//$title = isset($i_title)&&strlen($i_title)?($i_title):('%h: %s');
$title = '%h: %s';
if (isset($i_title) && $i_title==0) $title = null;
$geom = isset($i_geom)&&strpos($i_geom,'x')?explode('x',$i_geom):array(403,146); /* (500x200 on output) */
$width = isset($i_width)&&is_numeric($i_width)?floor($i_width):$geom[0];
$height = isset($i_height)&&is_numeric($i_height)?floor($i_height):$geom[1];

$time = rrd_time($time);

outputGraph($host, $service, $time, array('legend'=>($legend==1?true:false), 'title'=>$title, 'geom'=>array($width,$height)));
