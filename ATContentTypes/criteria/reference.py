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
""" Topic:

"""

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATReferenceCriterion'

from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import REFERENCE_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.criteria.selection import ATSelectionCriterion
from Products.Archetypes.atapi import DisplayList

ATReferenceCriterionSchema = ATSelectionCriterion.schema

class ATReferenceCriterion(ATSelectionCriterion):
    """A reference criterion"""

    __implements__ = ATSelectionCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    meta_type      = 'ATReferenceCriterion'
    archetype_name = 'Reference Criterion'
    shortDesc      = 'Select referenced content'


    def getCurrentValues(self):
        catalog = getToolByName(self, 'portal_catalog')
        uid_cat = getToolByName(self, 'uid_catalog')
        putils = getToolByName(self, 'plone_utils')
        options = catalog.uniqueValuesFor(self.Field())

        brains = uid_cat(UID=options, sort_on='Title')
        display = [((putils.pretty_title_or_id(b)).lower(), b.UID, b.Title or b.id) for b in brains]
        display.sort()
        display_list = DisplayList([(d[1], d[2]) for d in display])

        return display_list

registerCriterion(ATReferenceCriterion, REFERENCE_INDICES)
