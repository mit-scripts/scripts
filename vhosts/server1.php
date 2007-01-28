<?php
if (isset($_SERVER['SERVER_NAME'])) $name = $_SERVER['SERVER_NAME']; else $name = '';
if (isset($_SERVER['REQUEST_URI'])) $req = $_SERVER['REQUEST_URI']; else $req = '/';
if (isset($_SERVER['PATH_INFO'])) $pi = explode('/',$_SERVER['PATH_INFO']);
if (isset($_SERVER['SERVER_PORT'])) $port = $_SERVER['SERVER_PORT']; else $port = '80';

// catch a docroot from the DocumentRoot directive in an apacheconf
$documentRoot = str_replace(__FILE__,'',$_SERVER['DOCUMENT_ROOT']);
if (!empty($documentRoot) && substr($documentRoot,0,1) == '/')
	$documentRoot = substr($documentRoot, 1);
if (empty($documentRoot))
	$documentRoot = array_shift(explode('.',$_SERVER['SERVER_NAME']));

switch($port) {
	case 443:
		$myHTTP = 'https';
		$mySSL = true;
		break;
	default:
		$myHTTP = 'http';
		$mySSL = false;
		break;
}

$myTitle = $name;
$baseHTTP = 'http://scripts.mit.edu/~'.$documentRoot;
$baseHTTPS = 'https://scripts.mit.edu/~'.$documentRoot;

$settingsFile1 = '/afs/athena.mit.edu/contrib/scripts/vhosts/settings/'.$name;
$settingsFile2 = '/afs/athena.mit.edu/contrib/scripts/vhosts/settings/'.$name.'.mit.edu';
$settings = array();
file_exists($settingsFile1) && $settings = file($settingsFile1);
file_exists($settingsFile2) && $settings = file($settingsFile2);
if (count($settings)) {
	if (count($settings) >= 0 && '' != trim($settings[0])) $myTitle = trim($settings[0]);
	if (count($settings) >= 1 && '' != trim($settings[1])) $baseHTTP = trim($settings[1]);
	if (count($settings) >= 2 && '' != trim($settings[2])) $baseHTTPS = trim($settings[2]);
}

$baseURL = $mySSL?$baseHTTPS:$baseHTTP;
?>
<html>
<head><title><?=$myTitle?></title></head>

<frameset rows="*">
	<frame src="<?=$baseURL?><?=$req?>" />
</frameset>

</html>
