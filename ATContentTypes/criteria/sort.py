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

__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATSortCriterion'

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import SORT_INDICES
from Products.ATContentTypes.interfaces import IATTopicSortCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from Products.ATContentTypes import ATCTMessageFactory as _

ATSortCriterionSchema = ATBaseCriterionSchema + Schema((
    BooleanField('reversed',
                required=0,
                mode="rw",
                write_permission=ChangeTopics,
                default=0,
                widget=BooleanWidget(label=_(u'Reverse')),
                ),

    ))

class ATSortCriterion(ATBaseCriterion):
    """A sort criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSortCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATSortCriterionSchema
    meta_type      = 'ATSortCriterion'
    archetype_name = 'Sort Criterion'
    shortDesc      = 'Sort'

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = [('sort_on', self.Field())]

        if self.getReversed():
            result.append(('sort_order', 'reverse'))

        return tuple(result)

registerCriterion(ATSortCriterion, SORT_INDICES)
