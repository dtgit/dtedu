# -*- coding: utf-8 -*-
# $Id: __init__.py,v 1.11 2007/06/12 19:24:53 amelung Exp $
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
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

##from Products.CMFPlone.utils import ToolInit
##from Products.ECAssignmentBox.ECABTool import ECABTool
#
#from Products.ECAssignmentBox.config import *
#
#def initialize(context):
#	#ToolInit('ECAssignmentBox Utility Tool',
#	#		tools = (ECABTool,),
#	#		icon = 'ec_tool.png',
#	#	).initialize(context)
#	pass

__author__    = '''ma <amelung@iws.cs.uni-magdeburg.de>'''
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.11 $'

import os, os.path
from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFPlone.utils import ToolInit
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_module, allow_class, allow_type

import ECFolder, ECAssignmentBox, ECAssignmentTask, ECABTool
from Products.ECAssignmentBox.config import *


def initialize(context):
    # Import Types here to register them
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)
    
    # Add permissions to allow control on a per-class basis
    for i in range(0, len(content_types)):
        content_type = content_types[i].__name__
        if content_type in ADD_CONTENT_PERMISSIONS:
            context.registerClass(meta_type    = ftis[i]['meta_type'],
                                  constructors = (constructors[i],),
                                  permission   = ADD_CONTENT_PERMISSIONS[content_type])
