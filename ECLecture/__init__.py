# -*- coding: utf-8 -*-
# $Id: __init__.py,v 1.3 2006/04/12 12:25:10 amelung Exp $
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

from zLOG import LOG, INFO

LOG('ECLecture', INFO, 'Installing Product')

import os, os.path

from Globals import package_home

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

# local imports
from Products.ECLecture.config import *


registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    """
    """
    # Import Types here to register them
    from Products.ECLecture import content

    from AccessControl import ModuleSecurityInfo
    from AccessControl import allow_module, allow_class, allow_type

    content_types, constructors, ftis = process_types(
        listTypes(PRODUCT_NAME),
        PRODUCT_NAME)
    
    utils.ContentInit(
        PRODUCT_NAME + ' Content',
        content_types      = content_types,
        permission         = add_permission,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
