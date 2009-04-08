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
"""
"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.atapi import listTypes
from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.interfaces import IATTopic
from Products.ATContentTypes.interfaces import IATTopicCriterion

TYPE_ROLES = ('Manager', 'Owner')
TOPIC_ROLES = ('Manager',)
CHANGE_TOPIC_ROLES = TOPIC_ROLES + ('Owner',)
CRITERION_ROLES = ('Manager',)

# Gathering Topic and Event related permissions into one place
AddTopics = 'Add portal topics'
setDefaultRoles(AddTopics, TOPIC_ROLES)

ChangeTopics = 'Change portal topics'
setDefaultRoles(ChangeTopics, CHANGE_TOPIC_ROLES)

ChangeEvents = 'Change portal events'
setDefaultRoles(ChangeEvents, ('Manager', 'Owner',))

ModifyConstrainTypes = "Modify constrain types"
setDefaultRoles(ModifyConstrainTypes, ('Manager', 'Owner'))

ModifyViewTemplate = "Modify view template"
setDefaultRoles(ModifyViewTemplate, ('Manager', 'Owner'))

ViewHistory = "ATContentTypes: View history"
setDefaultRoles(ViewHistory, ('Manager', ))

UploadViaURL = "ATContentTypes: Upload via url"
setDefaultRoles(UploadViaURL, ('Manager', ))

permissions = {}
def wireAddPermissions():
    """Creates a list of add permissions for all types in this project
    
    Must be called **after** all types are registered!
    """
    global permissions
    atct_types = listTypes(PROJECTNAME)
    for atct in atct_types:
        if IATTopic.isImplementedByInstancesOf(atct['klass']):
            permission = AddTopics 
        elif IATTopicCriterion.isImplementedByInstancesOf(atct['klass']):
            permission = "%s Topic: Add %s" % (PROJECTNAME, atct['portal_type'])
            setDefaultRoles(permission, CRITERION_ROLES)
        else:
            permission = "%s: Add %s" % (PROJECTNAME, atct['portal_type'])
            setDefaultRoles(permission, TYPE_ROLES)
        
        permissions[atct['portal_type']] = permission
    return permissions
