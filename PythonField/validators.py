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
$Id: validators.py 8325 2007-08-10 13:12:36Z encolpe $
"""

from Products.validation import validation, interfaces
from Products.PythonScripts.PythonScript import PythonScript

class PythonValidator:
    """ Validator for Python scripts.

    If a PythonScript compiles it's a valid expression.  If it's
    invalid, we get a message with details.

    >>> validator = PythonValidator()
    >>> validator('True')
    1
    >>> validator("asd : asd")
    'invalid syntax (Script (Python), line 1)'
    >>> validator("foo ( bar")
    'unexpected EOF while parsing (Script (Python), line 1)'
    """

    __implements__ = (interfaces.ivalidator,)

    name = 'pythonvalidator'

    def __call__(self, value, *args, **kwargs):
        if not isinstance(value, PythonScript):
            script = PythonScript('no_id')
            script.ZPythonScript_edit('**options', value)
            value = script

        script._compile()
        if script.errors:
            return '<br/>\n'.join(script.errors)
        else:
            return 1

validation.register(PythonValidator())
