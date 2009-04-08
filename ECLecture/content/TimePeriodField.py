# -*- coding: utf-8 -*-
# $Id: TimePeriodField.py,v 1.3 2006/10/04 18:02:40 mxp Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
# ECLecture is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECLecture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECLecture; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import re

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import ObjectField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerField

from Products.validation import validation


from validators import TimePeriodValidator

# -- register time period validator -------------------------------------------
isTimePeriod = TimePeriodValidator("isTimePeriod")
validation.register(isTimePeriod)


class TimePeriodField(ObjectField):
    """
    A field that stores a list of two integer values representing 
    a time period
    """

    __implements__ = ObjectField.__implements__

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'integer',
        'size' : '5',
        'widget' : StringWidget,
        'default' : [],
        'validators' : ('isTimePeriod'),
        })

    security  = ClassSecurityInfo()

    security.declarePrivate('validate_required')
    def validate_required(self, instance, value, errors):
        """
        Tests if all elements in value are not None. If one is None a 
        error message will be returned.
        
        @see ObjectField.validate_required
        """
        result = True
        
        for item in value:
            if not item:
                result = False
                break

        return ObjectField.validate_required(self, instance, result, errors)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Tests if all elements in value are numbers and save them as minutes.
        
        @see ObjectField.set
        """
        result = []
        
        for item in value:
            if self.required or item:
                m = re.match('^(\d\d)[.:]?(\d\d)$', item.strip())
                result.append((int(m.group(1)) * 60 ) + int(m.group(2)))
            else:
                result = []
                break
        
        ObjectField.set(self, instance, result, **kwargs)


registerField(TimePeriodField,
              title='TimePeriod',
              description=('Stores a list of two integer values representing '
                           'a time period')
    )
