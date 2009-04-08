# -*- coding: utf-8 -*-
## GroupUserFolder
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

## Copyright (c) 2003 The Connexions Project, All Rights Reserved
## initially written by J Cameron Cooper, 11 June 2003
## concept with Brent Hendricks, George Runyan
"""
Basic usergroup tool.
"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: GroupsToolPermissions.py 30098 2006-09-08 12:35:01Z encolpe $
__docformat__ = 'restructuredtext'

# BBB CMF < 1.5
try:
    from Products.CMFCore.permissions import *
except ImportError:
    from Products.CMFCore.CMFCorePermissions import *

AddGroups = 'Add Groups'
setDefaultRoles(AddGroups, ('Manager',))

ManageGroups = 'Manage Groups'
setDefaultRoles(ManageGroups, ('Manager',))

ViewGroups = 'View Groups'
setDefaultRoles(ViewGroups, ('Manager', 'Owner', 'Member'))

DeleteGroups = 'Delete Groups'
setDefaultRoles(DeleteGroups, ('Manager', ))

SetGroupOwnership = 'Set Group Ownership'
setDefaultRoles(SetGroupOwnership, ('Manager', 'Owner'))
