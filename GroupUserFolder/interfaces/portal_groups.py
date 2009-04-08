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
"""Groups tool interface

Goes along the lines of portal_membership, but for groups.
"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: portal_groups.py 30098 2006-09-08 12:35:01Z encolpe $
__docformat__ = 'restructuredtext'


from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_groups(Interface):
    """Defines an interface for working with groups in an abstract manner.
    Parallels the portal_membership interface of CMFCore"""
##    id = Attribute('id','Must be set to "portal_groups"')

    def isGroup(u):
        """Test if a user/group object is a group or not.
        You must pass an object you get earlier with wrapUser() or wrapGroup()
        """

    def getGroupById(id):
        """Returns the portal_groupdata-ish object for a group corresponding
        to this id."""

    def getGroupsByUserId(userid):
        """Returns a list of the groups the user corresponding to 'userid' belongs to."""

    def listGroups():
        """Returns a list of the available portal_groupdata-ish objects."""

    def listGroupIds():
        """Returns a list of the available groups' ids (WITHOUT prefixes)."""

    def listGroupNames():
        """Returns a list of the available groups' names (ie. without prefixes)."""

##    def getPureUserNames():
##        """Get the usernames (ids) of only users. """

##    def getPureUsers():
##        """Get the actual (unwrapped) user objects of only users. """

    def searchForGroups(REQUEST, **kw):    # maybe searchGroups()?
        """Return a list of groups meeting certain conditions. """
        # arguments need to be better refined?

    def addGroup(id, roles = [], groups = [], **kw):
        """Create a group with the supplied id, roles, and groups.

        Underlying user folder must support adding users via the usual Zope API.
        Passwords for groups seem to be currently irrelevant in GRUF."""

    def editGroup(id, roles = [], groups = [], **kw):
        """Edit the given group with the supplied roles.

        Underlying user folder must support editing users via the usual Zope API.
        Passwords for groups seem to be currently irrelevant in GRUF.
        One can supply additional named parameters to set group properties."""

    def removeGroups(ids, keep_workspaces=0):
        """Remove the group in the provided list (if possible).

        Will by default remove this group's GroupWorkspace if it exists. You may
        turn this off by specifying keep_workspaces=true.
        Underlying user folder must support removing users via the usual Zope API."""

    def setGroupOwnership(group, object):
        """Make the object 'object' owned by group 'group' (a portal_groupdata-ish object)"""

    def setGroupWorkspacesFolder(id=""):
        """ Set the location of the Group Workspaces folder by id.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders.

        If anyone really cares, we can probably make the id work as a path as well,
        but for the moment it's only an id for a folder in the portal root, just like the
        corresponding MembershipTool functionality. """

    def getGroupWorkspacesFolderId():
        """ Get the Group Workspaces folder object's id.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders. """

    def getGroupWorkspacesFolder():
        """ Get the Group Workspaces folder object.

        The Group Workspaces Folder contains all the group workspaces, just like the
        Members folder contains all the member folders. """

    def toggleGroupWorkspacesCreation():
        """ Toggles the flag for creation of a GroupWorkspaces folder upon first
        use of the group. """

    def getGroupWorkspacesCreationFlag():
        """Return the (boolean) flag indicating whether the Groups Tool will create a group workspace
        upon the next use of the group (if one doesn't exist). """

    def getGroupWorkspaceType():
        """Return the Type (as in TypesTool) to make the GroupWorkspace."""

    def setGroupWorkspaceType(type):
        """Set the Type (as in TypesTool) to make the GroupWorkspace. Expects the name of a Type."""

    def createGrouparea(id):
        """Create a space in the portal for the given group, much like member home
        folders."""

    def getGroupareaFolder(id):
        """Returns the object of the group's work area."""

    def getGroupareaURL(id):
        """Returns the full URL to the group's work area."""

    # and various roles things...
