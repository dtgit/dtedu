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

from AccessControl import ClassSecurityInfo
from _tales import Expression, getExprContext
from Products.Archetypes.Field import encode
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Widget import LinesWidget
from Products.Archetypes.Registry import registerField

class TALESString(ObjectField):

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'tales',
        'default': 'python: True',
        'default_content_type' : 'text/plain',
        'required': True,
        'validators': ('talesvalidator',)
        })

    security  = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        # Get the Expression
        expr = ObjectField.get(self, instance, **kwargs)

        # use a custom context if it has been passed in
        context = kwargs.get('expression_context')
        if context is None:
            context = getExprContext(instance, instance)

        # Expression's __call__ returns a context dictionary if the
        # expression's text is an empty string.  We return None instead.
        if expr.text.strip():
            # Return the evaluated expression
            value = expr(context)
            return encode(value, instance, **kwargs)
        else:
            return None

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        # Get the Expression
        expr = ObjectField.get(self, instance, **kwargs)
        # Return the expression text
        return getattr(expr, 'text', expr)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if not isinstance(value, Expression.Expression):
            value = Expression.Expression(value)
        ObjectField.set(self, instance, value, **kwargs)

    def getDefault(self, instance):
        value = ObjectField.getDefault(self, instance)
        return Expression.Expression(value)

registerField(TALESString,
              title='TALES String',
              description=('A field that can take a TALES expression '
                           'and evaluate it.'))


class TALESLines(ObjectField):

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'taleslines',
        'default': ['python: True'],
        'widget': LinesWidget,
        'required': True,
        'validators': ('talesvalidator',)
        })

    security = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        # Get Expressions
        exprs = ObjectField.get(self, instance, **kwargs)

        # use a custom context if it has been passed in
        context = kwargs.get('expression_context')
        if context is None:
            context = getExprContext(instance, instance)

        # Return evaluated expressions, and check for empty expr texts.
        value = []
        for expr in exprs:
            if expr.text.strip():
                line = expr(context)
                value.append(encode(line, instance, **kwargs))
            else:
                value.append(None)
        return value

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        # Get Expressions
        exprs = ObjectField.get(self, instance, **kwargs)
        # Return text
        return [getattr(expr, 'text', expr) for expr in exprs]

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        value = [isinstance(expr, Expression.Expression) and expr or
                 Expression.Expression(expr) for expr in value]
        ObjectField.set(self, instance, value, **kwargs)

    def getDefault(self, instance):
        exprs = ObjectField.getDefault(self, instance)
        return [Expression.Expression(expr) for expr in exprs]

registerField(TALESLines,
              title='TALES Lines',
              description='A field that takes lines (i.e., a list) of TALES '
              'expressions and evalutes them.')
