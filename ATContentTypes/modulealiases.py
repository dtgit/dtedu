#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""Module aliases for unpickling

The dotted class path of most persistent classes were changed before version 1.0
beta. This module creates aliases using sys.modules for unpickling old objects.
"""
__author__  = ''
__docformat__ = 'restructuredtext'

import sys
from types import ModuleType

from Products.ATContentTypes import content
from Products.ATContentTypes.content import link
from Products.ATContentTypes.content import image
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import file
from Products.ATContentTypes.content import event
from Products.ATContentTypes.content import newsitem
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import favorite
from Products.ATContentTypes.content import topic

from Products.ATContentTypes import criteria
from Products.ATContentTypes.criteria import boolean
from Products.ATContentTypes.criteria import date
from Products.ATContentTypes.criteria import daterange
# do not import the module with a builtin name 'list' as this makes a mess
from Products.ATContentTypes.criteria import list as list_criteria
from Products.ATContentTypes.criteria import portaltype
from Products.ATContentTypes.criteria import reference
from Products.ATContentTypes.criteria import selection
from Products.ATContentTypes.criteria import simpleint
from Products.ATContentTypes.criteria import simplestring
from Products.ATContentTypes.criteria import sort
from Products.ATContentTypes import interface

def createModuleAliases():
    """Creates module aliases in sys.modules

    Aliases are created for Products.ATContentTypes.types and all modules below
    it which contain classes with persistent objects (content types) but for
    modules with base classes and schemata.

    It might look a little bit tricky but it's very easy. The method is
    iterating over all modules in the module name space (globals) and creating
    aliases only forthoses modules which are modules with the module name starting with
    Products.ATContentTypes. All these modules have a module level var called
    "__old_name__".
    """
    for module in globals().values():
        if type(module) is not ModuleType:
            # not a module
            continue
        name = module.__name__
        if not name.startswith('Products.ATContentTypes'):
            # not a module inside ATCT
            continue
        old_name = getattr(module, '__old_name__', None)
        if old_name is None:
            continue
        sys.modules[old_name] = module

# Aliase for EXIF classes
import exif
sys.modules['Products.ATContentTypes.lib.exif'] = exif
sys.modules['Products.ATContentTypes.z3.interfaces'] = interface

createModuleAliases()
