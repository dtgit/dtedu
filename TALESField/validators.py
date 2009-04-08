##############################################################################
#
# TALESField - Field with TALES support for Archetypes
# Copyright (C) 2005 Sidnei da Silva, Daniel Nouri and contributors
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
$Id: __init__.py,v 1.2 2005/02/26 17:56:10 sidnei Exp $
"""

from Products.validation import validation, interfaces
from Products.PageTemplates.Expressions import getEngine
try:
    from zope.tales.tales import CompilerError
except ImportError:
    # BBB for Zope <2.10, will be removed in Zope 2.12
    from Products.PageTemplates.TALES import CompilerError

class TALESValidator:
    """ Validator for TALES Expressions

    Basically, if the expression compiles it's a valid expression,
    otherwise it's invalid and you get a message saying that the
    expression has errors.

    >>> validator = TALESValidator()
    >>> validator('python: True')
    1

    >>> validator('foo: bar')
    'TALES expression "foo: bar" has errors.'

    >>> validator('string: Yes')
    1

    Try a SyntaxError:

    >>> validator('python: True False')
    'TALES expression "python: True False" has errors.'

    Unbalanced parens:

    >>> validator('python: 1 + (4 * 5')
    'TALES expression "python: 1 + (4 * 5" has errors.'

    Trash:

    >>> validator('xdfaydf asdf')
    'TALES expression "xdfaydf asdf" has errors.'

    The validator also accepts lists of expressions:

    >>> validator(['python: True', 'xdfaydf asdf'])
    'TALES expression "xdfaydf asdf" has errors.'
    """

    __implements__ = (interfaces.ivalidator,)

    name = 'talesvalidator'

    def __call__(self, value, *args, **kwargs):
        if type(value) != type([]) and type(value) != type(()):
            value=(value,)
        for expr in value:
            try:
                if expr.strip():
                    getEngine().compile(expr)
            except CompilerError, e:
                return 'TALES expression "%s" has errors.' % expr
        return 1

validation.register(TALESValidator())
