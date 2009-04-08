## Script (Python) "str"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: str.py,v 1.1 2006/08/10 13:16:18 wfenske Exp $
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

""" Converts objetcs into strings encoded in Plone's default character set """

if same_type(obj, '') or same_type(obj, u''):
    value = obj
else:
    value = str(obj)
    
return context.unicodeDecode(value).encode( context.getCharset() )
