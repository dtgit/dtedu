##############################################################################
#
# ATContentTypes http://plone.org/products/atcontenttypes/
# Archetypes reimplementation of the CMF core types
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2006 AT Content Types development team
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Topic:


"""

__author__  = 'Alec Mitchell <apm13@columbia.edu>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATCurrentAuthorCriterion'

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.criteria import registerCriterion, \
                                             LIST_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

ATCurrentAuthorSchema = ATBaseCriterionSchema

class ATCurrentAuthorCriterion(ATBaseCriterion):
    """A criterion that searches for the currently logged in user's id"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATCurrentAuthorSchema
    meta_type      = 'ATCurrentAuthorCriterion'
    archetype_name = 'Current Author Criterion'
    shortDesc      = 'Restrict to current user'

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        user = getToolByName(self, 'portal_membership').getAuthenticatedMember().getId()

        if user is not '':
            result.append((self.Field(), user))

        return tuple( result )

registerCriterion(ATCurrentAuthorCriterion, LIST_INDICES)
