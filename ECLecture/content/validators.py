# -*- coding: utf-8 -*-
# $Id: validators.py,v 1.2 2006/04/12 12:25:12 amelung Exp $
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

try:
    from Products.validation.interfaces.IValidator import IValidator
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
    from interfaces.IValidator import IValidator
    del sys, os


class TimePeriodValidator:
    """
    Ensure that we don't get a value for start and/or end time of a time period
    which are not valid.
    """
    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
    
    def __call__(self, value, *args, **kwargs):
        """
        """
        if value[0] or value[1]:

            for item in value:
                m = re.match('^\s*(\d\d)[.:]?(\d\d)\s*$', item)
    
                if not m:
                    return ("Validation failed: '%(value)s' is not a time specification." %
                            { 'value': item, })
        
        return True
        
