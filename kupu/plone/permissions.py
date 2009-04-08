##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Zope2 permissions for server-side Kupu interaction

$Id: permissions.py 36159 2007-01-05 08:50:23Z duncan $
"""
try:
    from Products.CMFCore.permissions import setDefaultRoles
except ImportError:
    # for CMF 1.4
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles

QueryLibraries = "Kupu: Query libraries"
ManageLibraries = "Kupu: Manage libraries"

# Set up default roles for permissions
setDefaultRoles(QueryLibraries, ('Manager', 'Authenticated'))
setDefaultRoles(ManageLibraries, ('Manager',))
