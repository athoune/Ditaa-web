What is Ditaa
=============

[Ditaa](http://ditaa.sourceforge.net/) is a magical wand wich convert ascii-art scheme into nice picture.
The original tool only work as a command line tool.
This variants bring ditaa to webservice hype.

Now, ditaa  can be efficiently used from a webserver (as a wiki filter), even in a mutualised server.

Use DAS, Ditaa As a Service
===========================

Put ditaa\_web.war in your favorite servlet container (glassfish, jetty, tomcat ...).
From the client side, Ditaa is accessed with a simple POST request with this arguments :

 * _ditaa_ the scheme.
 * _no-antialias_
 * _no-shadows_
 * _scale_
 * _round-corners_
 * _no-separations_

Don't forget to add caching.

A PHP and Python example are provided.

Build it
========

This project is a lazy **netbeans** project. You can import it and build it.
If you don't care about netbeans, juste use **ant** :

	$ ant
	$ ls dist
	ditaa_web.war   javadoc

Snow leopard user have to update their ant, 1.7 is not enough, Netbeans projects wont 1.7.1. **Macport** provides the right ant.