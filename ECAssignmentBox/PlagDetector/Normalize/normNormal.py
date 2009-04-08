# -*- coding: utf-8 -*-
# $Id: normNormal.py,v 1.1 2007/07/02 14:40:25 peilicke Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

#coding: latin-1
#
#Author: Christian Dervaric
#
#Description:
#
#Calling normalize(string) will normalize natural language texts in the manner
#that all non alphanumerical characters will be deleted. The letters will be 
#transformed to lower case. All white spaces are reduced to 1.

from Products.ECAssignmentBox.PlagDetector.errors import NoValidArgumentError
import re



#pattern = re.compile(r'\W+', re.L)
pattern = re.compile(r'[^A-Za-z0-9äüöß]+') #TODO: anpassen an alle Sprachsätze?
#pattern = re.compile("^\w+", re.L)

def normalize(string):
    """Takes a String and removes all non-alpha-numeric elements. It also 
        reduces white spaces to 1. And it sets all words to lower case.
    """
    #check for valid string argument
    if string == '':
        return ''
    elif type(string) != type(''):
        raise NoValidArgumentError, 'Input must be of type String.'
    
    #normalize the string
    list = pattern.split(string)    #splits string to alphanumeric words
    list = map(lambda s: s.lower(), list)    #transforms all strings to lowercase
    return ' '.join(list)    #return string
