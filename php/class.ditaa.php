<?php

//http://netevil.org/blog/2006/nov/http-post-from-php-without-curl

function do_post_request($url, $args, $optional_headers = null) {
	$data = "";
	foreach($args as $key=>$value)
		$data .= '&' . $key . '=' . urlencode($value);
	$params = array(
		'http' => array(
			'method' => 'POST',
			'content' => substr($data,1)
		));
	if ($optional_headers !== null)
		$params['http']['header'] = $optional_headers;
	$ctx = stream_context_create($params);
	$fp = @fopen($url, 'rb', false, $ctx);
	if (!$fp)
		throw new Exception("Problem with $url, $php_errormsg");
	$response = @stream_get_contents($fp);
	if ($response === false)
		throw new Exception("Problem reading data from $url, $php_errormsg");
	return $response;
}

class Ditaa {
	
	function __construct($url) {
		$this->url = $url;
		$this->antialias = true;
		$this->shadows = true;
		$this->scale = 1;
		$this->round_corners = false;
		$this->separations = true;
	}
	function buildImage($ditaa) {
		$args = array();
		$args['ditaa'] = $ditaa;
		$args['no-antialias'] = $this->antialias ? 0:1;
		$args['no-shadows'] = $this->shadows ? 0:1;
		$args['scale'] = $this->scale;
		$args['round-corners'] = $this->round_corners ? 1:0;
		$args['no-separations'] = $this->separations ? 0:1;
		return do_post_request($this->url, $args);
	}
	function saveImage($ditaa, $path) {
		$local = fopen($path, 'wb');
		fwrite($local, $this->buildImage($ditaa));
		fclose($local);
	}
}
?>
