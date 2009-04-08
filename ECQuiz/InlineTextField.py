# -*- coding: iso-8859-1 -*-
#
# $Id: InlineTextField.py,v 1.1 2006/08/10 13:16:06 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from xml.dom.minidom import parseString

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner
from OFS.content_types import guess_content_type

from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import TextField

from tools import log

class InlineTextField(TextField):
    """ A TextField puts the contents in a <p>-element if the content type is 
        'text/plain', 'text/structured' or 'text/restructured' and the
        default_output_type is 'text/html'. This class behaves exactly like 
        TextField, except it does remove those additional <p> tags.
    """
    def get(self, instance, mimetype=None, raw=False, forceInline=False, **kwargs):
        data = TextField.get(self, instance)
        if(raw or (not forceInline)):
            return data
        if(isinstance(data, str) or isinstance(data, unicode)):
            try:
                doc = parseString( '<x>%s</x>' % data.strip() )
                root = doc.documentElement
                for child in root.childNodes:
                    if( (child.nodeType == child.TEXT_NODE) and 
                        child.data.strip() ):
                        break
                    elif( child.nodeType == child.ELEMENT_NODE ):
                        style = child.getAttribute('style')
                        child.setAttribute('style', u'display:inline;' + style)
                        ## IE hack start ##
                        child.appendChild( doc.createTextNode(' ') )
                        ## IE hack end ##
                        break
                tmp = ''
                for child in root.childNodes:
                    tmp += child.toxml()
                doc.unlink()                
                data = tmp
            except:
                pass
        return data
    

# Register this field in Zope
try:
    registerField(InlineTextField,
              title='Inline Text',
              description=('Used for storing text which can be '
                           'used in transformations'))
    log('Worked: registerField(InlineTextField)\n')
except Exception, e:
    log('Failed: registerField(InlineTextField): ' + unicode(e) + '\n')
    raise e
