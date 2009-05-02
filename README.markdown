What is Ditaa
=============

[Ditaa](http://ditaa.sourceforge.net/) is a magical wand wich convert ascii-art scheme into nice picture.
The original tool only work as a command line tool.
This variants bring ditaa to webservice hype.

Now, ditaa  can be efficiently used from a webserver (as a wiki filter), even in a mutualised server.

Use DAS, Ditaa As a Service
===========================

Put ditaa_web.war in your favorite servlet container (glassfish, jetty, tomcat ...).
From the client side, Ditaa is accessed with a simple POST request with this arguments :
 * _ditaa_ the scheme.
 * _no-antialias_
 * _no-shadows_
 * _scale_
 * _round-corners_
 * _no-separations_

Don't forget to add caching.

A PHP example is provided.