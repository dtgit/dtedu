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

__author__  = 'Godefroid Chapelle'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATPortalTypeCriterion'

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import DisplayList

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import FIELD_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.criteria.selection import ATSelectionCriterion

from Products.ATContentTypes import ATCTMessageFactory as _

ATPortalTypeCriterionSchema = ATSelectionCriterion.schema.copy()

val_widget = ATPortalTypeCriterionSchema['value'].widget
val_widget.description=_(u'help_portal_type_criteria_value',
                         default=u'One of the available content types.')
ATPortalTypeCriterionSchema['value'].widget = val_widget

    
class ATPortalTypeCriterion(ATSelectionCriterion):
    """A portal_types criterion"""

    __implements__ = ATSelectionCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATPortalTypeCriterionSchema
    meta_type      = 'ATPortalTypeCriterion'
    archetype_name = 'Portal Types Criterion'
    shortDesc      = 'Select content types'

    security.declareProtected(View, 'getCurrentValues')
    def getCurrentValues(self):
         """Return enabled portal types"""
         plone_tool = getToolByName(self, 'plone_utils')
         portal_types = plone_tool.getUserFriendlyTypes()
         getSortTuple = lambda x: ((x.Title() or x).lower(),
           unicode(x.Title() or x), x.Title() or x)

         if self.Field() == 'Type':
            types_tool = getToolByName(self, 'portal_types')
            get_type = types_tool.getTypeInfo
            # first item in tuple is sortkey, second is untranslated Title
            # and third is Title as a translatable Message object
            portal_types = [getSortTuple(get_type(t)) for t in portal_types]
         else:
            portal_types = [(t.lower(), t, t) for t in portal_types]

         portal_types.sort()
         portal_types = [(p[1], p[2]) for p in portal_types]
         return DisplayList(portal_types)

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.Value() is not '':
            result.append((self.Field(), self.Value()))

        return tuple(result)

registerCriterion(ATPortalTypeCriterion, FIELD_INDICES)
