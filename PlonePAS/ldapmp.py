##############################################################################
#
# PlonePAS - Adapt PluggableAuthService for use in Plone
# Copyright (C) 2005 Enfold Systems, Kapil Thangavelu, et al
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
"""

from Products.PlonePAS.patch import call, wrap_method
from Products.PlonePAS.plugins.group import PloneGroup
from Products.LDAPMultiPlugins.LDAPPluginBase import LDAPPluginBase
from Products.LDAPMultiPlugins.LDAPMultiPlugin import LDAPMultiPlugin

from sets import Set

GROUP_PROPERTY_MAP = {
    # target property: (possible key, ...)
    'title': ('name',
              'displayName',
              'cn',),
    'description': ('description', ),
    'email': ('mail', ),
    }

KNOWN_ATTRS = []
for attrs in GROUP_PROPERTY_MAP.values():
    for attr in attrs:
        KNOWN_ATTRS.append(attr)
KNOWN_ATTRS = Set(KNOWN_ATTRS)

def getPropertiesForUser(self, user, request=None):
    """Fullfill PropertiesPlugin requirements
    """

    if not isinstance(user, PloneGroup):
        # It's not a PloneGroup, continue as usual
        return call(self, 'getPropertiesForUser', user=user, request=request)

    # We've got a PloneGroup.
    # Search for groups instead of users
    groups = self.enumerateGroups(id=user.getId(), exact_match=True)
    # XXX Should we assert there's only one group?
    properties = {}
    for group in groups:
        for pname, attrs in GROUP_PROPERTY_MAP.items():
            for attr in attrs:
                value = group.get(attr)
                if value:
                    # Break on first found
                    properties[pname] = value
                    break

    return properties

wrap_method(LDAPPluginBase, 'getPropertiesForUser', getPropertiesForUser)

def getGroupsForPrincipal(self, user, request=None, attr=None):
    """ Fulfill GroupsPlugin requirements, but don't return any groups for groups """

    if not isinstance(user, PloneGroup):
        # It's not a PloneGroup, continue as usual
        return call(self, 'getGroupsForPrincipal', user, request=request, attr=attr)

    return ()

wrap_method(LDAPMultiPlugin, 'getGroupsForPrincipal', getGroupsForPrincipal)
