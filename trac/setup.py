"""
$Id$
$HeadURL$

Copyright (c) 2005, 2006, 2008 Peter Kropf. All rights reserved.

Python egg setup file for the graphviz trac wiki processor.
"""


__revision__  = '$LastChangedRevision$'
__id__        = '$Id$'
__headurl__   = '$HeadURL$'
__docformat__ = 'restructuredtext'
__version__   = '0.1'

from setuptools import setup, find_packages

setup (
    name = 'ditaatrac',
    version = __version__,
    packages = find_packages(),
    entry_points={'trac.plugins': 'ditaatrac = ditaatrac'},
    author = "Mathieu Lecarme",
    author_email = "mathieu@garambrogne.net",
    keywords = "trac ditaa",
#    url = "http://trac-hacks.org/wiki/GraphvizPlugin",
    description = "Ditaa plugin for Trac 0.11",
    long_description = """
    """,
    license = """
    """,
)
