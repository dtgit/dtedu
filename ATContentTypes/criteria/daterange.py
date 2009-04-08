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
__old_name__ = 'Products.ATContentTypes.types.criteria.ATDateRangeCriterion'

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import CalendarWidget

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import DATE_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from Products.ATContentTypes import ATCTMessageFactory as _

RELEVANT_INDICES=list(DATE_INDICES)
RELEVANT_INDICES.remove('DateRangeIndex')
RELEVANT_INDICES = tuple(RELEVANT_INDICES)

ATDateRangeCriterionSchema = ATBaseCriterionSchema + Schema((
    DateTimeField('start',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                widget=CalendarWidget(
                    label=_(u'label_date_range_criteria_start', default=u'Start Date'),
                    description=_(u'help_date_range_criteria_start',
                                  default=u'The beginning of the date range to search')
                    ),
                ),
    DateTimeField('end',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default=None,
                widget=CalendarWidget(
                    label=_(u'label_date_range_criteria_end', default=u'End Date'),
                    description=_(u'help_date_range_criteria_end',
                                  default=u'The ending of the date range to search.')

                    ),
                ),
    ))

class ATDateRangeCriterion(ATBaseCriterion):
    """A date range criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATDateRangeCriterionSchema
    meta_type      = 'ATDateRangeCriterion'
    archetype_name = 'Date Range Criterion'
    shortDesc      = 'Date range'

    security.declareProtected(View, 'Value')
    def Value(self):
        return (self.getStart(), self.getEnd())

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        field = self.Field()
        value = self.Value()

        return ( ( field, {'query': value, 'range': 'min:max'} ), )

registerCriterion(ATDateRangeCriterion, RELEVANT_INDICES)
