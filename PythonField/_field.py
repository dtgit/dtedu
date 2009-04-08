##############################################################################
#
# PythonField - Field with Python support for Archetypes
# Copyright (C) 2005 Klein & Partner KEG
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
$Id: _field.py 7383 2007-01-26 09:24:39Z yenzenz $
"""

from AccessControl import ClassSecurityInfo
from Products.PythonScripts.PythonScript import PythonScript

from Products.Archetypes.public import ObjectField, TextAreaWidget
from Products.Archetypes.Registry import registerField

class PythonWidget(TextAreaWidget):
    
    __implements__ = TextAreaWidget.__implements__

    _properties = TextAreaWidget._properties.copy()
    _properties.update({
        'visible' : {'view': 'invisible', 'edit': 'visible'},
    })

class PythonField(ObjectField):

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'python',
        'default': 'pass',
        'default_content_type' : 'text/plain',
        'required': True,
        'widget': PythonWidget,
        'validators': ('pythonvalidator',),
        'header': '',
        'footer': '',
        })

    _seperator = "# PythonField seperator\n"

    security  = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        script = ObjectField.get(self, instance, **kwargs)
        return script(**kwargs)

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        body = ObjectField.get(self, instance, **kwargs).body()
        p1 = body.find(self._seperator)
        if p1 == -1:
            # no seperator: we return the whole body
            return body
        else:
            p1 = p1 + len(self._seperator)
            p2 = body.find(self._seperator, p1)
            return body[p1:p2]

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if not isinstance(value, PythonScript):
            s = self._seperator
            body = "%s\n%s%s\n%s%s" % (self.header, s, value, s, self.footer)
            script = PythonScript(self.getName())
            script.ZPythonScript_edit('**options', body)
            value = script
        ObjectField.set(self, instance, value, **kwargs)

    def getDefault(self, instance):
        value = ObjectField.getDefault(self, instance)
        script = PythonScript(self.getName())
        script.ZPythonScript_edit('**options', value)
        return script.__of__(instance)

registerField(
    PythonField,
    title="Python Field",
    description=("A field that stores Python Scripts")
    )
