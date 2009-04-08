# -*- coding: iso-8859-1 -*-
#
# $Id: XMLValidator.py,v 1.1 2006/08/10 13:16:06 wfenske Exp $
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

""" A validator for XML fragments, i.e. stuff like

    <p>Paragraph</p>
    This is <strong>very</strong> important.
"""

from Products.validation.interfaces import ivalidator
from xml.dom.minidom import parseString

from tools import log
from tools import registerValidatorLogged

class XMLValidator:
    """A validator for XML fragments."""
    
    __implements__ = (ivalidator,)
    
    def __init__(self, name):
        self.name = name
    
    def __call__(self, value, *args, **kwargs):
        # First we have to find out if this is meant to be text/html
        instance = kwargs.get('instance', None)
        field    = kwargs.get('field',    None)
        if instance and field:
            request     = getattr(instance, 'REQUEST', None)
            formatField = "%s_text_format" % field.getName()
            if request and ( request.get(formatField, 
                '').strip().lower() == 'text/html' ):
                # Aha! The format was set to 'text/html'
                if isinstance(value, str):
                    string = '<a>' + value + '</a>'
                else:
                    string = u'<a>' + value + u'</a>'
                try:
                    doc = parseString(string)
                    doc.unlink() # Destroy the document object so the garbage
                    # collector can delete it
                    return 1
                except:
                    return """Please use XHTML conformant markup."""
        # The format was not 'text/html' or something went wrong
        return True

# Register this validator in Zope
registerValidatorLogged(XMLValidator, 'isXML')
