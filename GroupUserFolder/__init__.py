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
"""

"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: __init__.py 40111 2007-04-01 09:12:57Z alecm $
__docformat__ = 'restructuredtext'

# postonly protections
try:
    # Zope 2.8.9, 2.9.7 and 2.10.3 (and up)
    from AccessControl.requestmethod import postonly
except ImportError:
    try:
        # Try the hotfix too
        from Products.Hotfix_20070320 import postonly
    except:
        def postonly(callable): return callable


import GroupUserFolder
import GRUFFolder
try:
    import Products.LDAPUserFolder
    hasLDAP = 1
except ImportError:
    hasLDAP = 0
from global_symbols import *

# Plone import try/except
try:
    from Products.CMFCore.DirectoryView import registerDirectory
    import GroupsToolPermissions
except:
    # No registerdir available -> we ignore
    pass

# Used in Extension/install.py
global groupuserfolder_globals
groupuserfolder_globals=globals()

# LDAPUserFolder patching
if hasLDAP:
    import LDAPGroupFolder
    
    def patch_LDAPUF():
        # Now we can patch LDAPUF
        from Products.LDAPUserFolder import LDAPUserFolder
        import LDAPUserFolderAdapter
        LDAPUserFolder._doAddUser = LDAPUserFolderAdapter._doAddUser
        LDAPUserFolder._doDelUsers = LDAPUserFolderAdapter._doDelUsers
        LDAPUserFolder._doChangeUser = LDAPUserFolderAdapter._doChangeUser
        LDAPUserFolder._find_user_dn = LDAPUserFolderAdapter._find_user_dn
        LDAPUserFolder.manage_editGroupRoles = LDAPUserFolderAdapter.manage_editGroupRoles
        LDAPUserFolder._mangleRoles = LDAPUserFolderAdapter._mangleRoles

    # Patch LDAPUF  : XXX FIXME: have to find something cleaner here?
    patch_LDAPUF()

def initialize(context):

    try:
        registerDirectory('skins', groupuserfolder_globals)
    except:
        # No registerdir available => we ignore
        pass

    context.registerClass(
        GroupUserFolder.GroupUserFolder,
        permission='Add GroupUserFolders',
        constructors=(GroupUserFolder.manage_addGroupUserFolder,),
        icon='www/GroupUserFolder.gif',
        )

    if hasLDAP:
        context.registerClass(
            LDAPGroupFolder.LDAPGroupFolder,
            permission='Add GroupUserFolders',
            constructors=(LDAPGroupFolder.addLDAPGroupFolderForm, LDAPGroupFolder.manage_addLDAPGroupFolder,),
            icon='www/LDAPGroupFolder.gif',
            )

    context.registerClass(
        GRUFFolder.GRUFUsers,
        permission='Add GroupUserFolder',
        constructors=(GRUFFolder.manage_addGRUFUsers,),
        visibility=None,
        icon='www/GRUFUsers.gif',
        )

    context.registerClass(
        GRUFFolder.GRUFGroups,
        permission='Add GroupUserFolder',
        constructors=(GRUFFolder.manage_addGRUFGroups,),
        visibility=None,
        icon='www/GRUFGroups.gif',
        )

    try:
        from Products.CMFCore.utils import ToolInit, ContentInit
        from GroupsTool import GroupsTool
        from GroupDataTool import GroupDataTool
        ToolInit( meta_type='CMF Groups Tool'
                  , tools=( GroupsTool, GroupDataTool, )
                  , icon="tool.gif"
                  ).initialize( context )

    except ImportError:
        Log(LOG_NOTICE, "Unable to import GroupsTool and/or GroupDataTool. \
        This won't disable GRUF but if you use CMF/Plone you won't get benefit of its special features.")
