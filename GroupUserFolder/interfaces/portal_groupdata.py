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

Goes along the lines of portal_memberdata, but for groups.
"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: portal_groupdata.py 30098 2006-09-08 12:35:01Z encolpe $
__docformat__ = 'restructuredtext'

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_groupdata(Interface):
    """ A helper tool for portal_groups that transparently adds
    properties to groups and provides convenience methods"""

##    id = Attribute('id', "Must be set to 'portal_groupdata'")

    def wrapGroup(g):
        """ Returns an object implementing the GroupData interface"""


class GroupData(Interface):
    """ An abstract interface for accessing properties on a group object"""

    def setProperties(properties=None, **kw):
        """Allows setting of group properties en masse.
        Properties can be given either as a dict or a keyword parameters list"""

    def getProperty(id):
        """ Return the value of the property specified by 'id' """

    def getProperties():
        """ Return the properties of this group. Properties are as usual in Zope."""

    def getGroupId():
        """ Return the string id of this group, WITHOUT group prefix."""

    def getMemberId():
        """This exists only for a basic user/group API compatibility
        """

    def getGroupName():
        """ Return the name of the group."""

    def getGroupMembers():
        """ Return a list of the portal_memberdata-ish members of the group."""

    def getAllGroupMembers():
        """ Return a list of the portal_memberdata-ish members of the group
        including transitive ones (ie. users or groups of a group in that group)."""

    def getGroupMemberIds():
        """ Return a list of the user ids of the group."""

    def getAllGroupMemberIds():
        """ Return a list of the user ids of the group.
        including transitive ones (ie. users or groups of a group in that group)."""

    def addMember(id):
        """ Add the existing member with the given id to the group"""

    def removeMember(id):
        """ Remove the member with the provided id from the group """

    def getGroup():
        """ Returns the actual group implementation. Varies by group
        implementation (GRUF/Nux/et al)."""
