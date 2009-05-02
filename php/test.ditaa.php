<?php
include 'class.ditaa.php';

$ditaa = new Ditaa('http://admin.garambrogne.net/ditaa_web/ditaa');
$ditaa->round_corners = true;
$ditaa->scale = 1.5;
$ditaa->saveImage('
+-----------+
| Php rulez |
+-----------+', '/tmp/php_ditaa.png');
?>
