## Script (Python) "unicodeDecode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=string, defaultCharSet=None

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: unicodeDecode.py,v 1.1 2006/08/10 13:16:18 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
    
if(same_type(string, u'')):
    return string
elif(not same_type(string, '')):
    string = str(string)
    
charSetList = []
if defaultCharSet:
    charSetList += [defaultCharSet]
# Get Plone's 'default_charset' (The 'getCharset()' method is either inherited
# from Products.Archetypes.BaseObject or is acquired from the 'getCharset' 
# script (Python) in Archetypes/skins/archetypes/getCharset.py)
siteCharSet = context.getCharset()
        
if siteCharSet:
    charSetList += [siteCharSet]
charSetList += ['latin-1', 'utf-8', 'cp850', 'cp437', 'cp1252']
for charSet in charSetList:
    try:
        return unicode(string, charSet)
    except UnicodeError:
        pass
raise UnicodeError('Unable to decode %s' % string)
