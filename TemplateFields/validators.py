##############################################################################
#
# TemplateFields - DTML and ZPT fields for Archetypes
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
$Id: validators.py 9783 2008-06-10 11:54:26Z wichert $
"""

from Products.validation import validation, interfaces

from OFS.DTMLMethod import DTMLMethod
from DocumentTemplate.DT_Util import ParseError
from Products.PageTemplates.PageTemplate import PageTemplate

class DTMLValidator:
    """ Validator for DTML Methods.

    >>> validator = DTMLValidator()
    >>> validator("<dtml-var title_or_id>")
    1
    >>> validator("<dtml-spam>")
    'Unexpected tag, for tag &lt;dtml-spam&gt;, on line 1 of &lt;string&gt;'
    """

    __implements__ = (interfaces.ivalidator,)
    name = 'dtmlvalidator'

    def __call__(self, value, *args, **kwargs):
        if not isinstance(value, DTMLMethod):
            dtml = DTMLMethod('no_id')
            dtml.raw = value
            value = dtml
        try:
            value.parse(value.read())
        except ParseError, e:
            return e
        else:
            return 1

validation.register(DTMLValidator())

from Acquisition import Implicit

class AqPageTemplate(PageTemplate, Implicit):
    """Dynamic page template for ATDynDocument
    """

class ZPTValidator:
    """ Validator for Zope Page Templates.

    >>> validator = ZPTValidator()
    >>> validator("<span tal:replace='here/title_or_id' />")
    1
    >>> res = validator("<span tal:foobar='here' />")
    >>> res.startswith("Compilation failed")
    True
    >>> res = validator("<!spam>")
    >>> res.startswith("Compilation failed")
    True
    """

    __implements__ = (interfaces.ivalidator,)
    name = 'zptvalidator'

    def __call__(self, value, *args, **kwargs):
        if not isinstance(value, PageTemplate):
            pt = AqPageTemplate()
            if "instance" in kwargs:
                pt = pt.__of__(kwargs["instance"])
            pt.write(value)
            value = pt

        errors = value.pt_errors()
        if errors:
            return '<br/>\n'.join(errors)
        else:
            return 1

validation.register(ZPTValidator())
