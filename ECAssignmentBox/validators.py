# -*- coding: utf-8 -*-
# $Id: validators.py,v 1.2 2006/02/10 08:10:48 amelung Exp $
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

try:
    from Products.validation.interfaces.IValidator import IValidator
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
    from interfaces.IValidator import IValidator
    del sys, os


class PositiveNumberValidator:
    """
    """
    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
    
    def __call__(self, value, *args, **kwargs):
        try:
            nval = float(value)
        except ValueError:
            return ("Validation failed (%(name)s): could not convert \
            '%(value)r' to number" % { 'name' : self.name, 'value': value})

        if nval >= 0:
            return True

        return ("Validation failed: '%(value)s' is not a positive number." %
                { 'value': value, })
