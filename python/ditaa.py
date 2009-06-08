#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__version__ = '0.1'

import urllib

class Ditaa:
  antialias = True;
  shadows = True;
  scale = 1;
  round_corners = False;
  separations = True;
  def __init__(self, url):
    self.url = url
  def buildImage(self, ditaa):
    return urllib.urlopen(self.url, urllib.urlencode({
    'ditaa': ditaa,
    'no-antialias': not self.antialias,
    'no-shadows': not self.shadows,
    'scale': self.scale,
    'round-corners': self.round_corners,
    'no-separations': not self.separations
    }))
  def saveImage(self, ditaa, path):
    f = open(path, 'w')
    f.write(self.buildImage(ditaa).read())
    f.close()
if __name__ == '__main__':
  ditaa = Ditaa('http://admin.garambrogne.net/ditaa_web/ditaa')
  ditaa.round_corners = True
  ditaa.scale = 1.5
  ditaa.saveImage('''
  +--------------+
  | Python rulez |
  +--------------+''', '/tmp/python_ditaa.png')
  