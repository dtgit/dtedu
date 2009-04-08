##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Simple string-matching criterion class

$Id: SimpleStringCriterion.py 77186 2007-06-28 19:06:19Z yuppie $
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zope.interface import implements

from AbstractCriterion import AbstractCriterion
from interfaces import Criterion as z2ICriterion
from interfaces import ICriterion
from permissions import ChangeTopics
from permissions import View
from Topic import Topic


class SimpleStringCriterion( AbstractCriterion ):

    """ Represent a simple field-match for a string value.
    """

    implements(ICriterion)
    __implements__ = z2ICriterion

    meta_type = 'String Criterion'

    security = ClassSecurityInfo()

    _editableAttributes = ( 'value', )

    def __init__(self, id, field):
        self.id = id
        self.field = field
        self.value = ''

    security.declareProtected( ChangeTopics, 'getEditForm' )
    def getEditForm( self ):
        """
            Return the skinned name of the edit form.
        """
        return 'ssc_edit'

    security.declareProtected( ChangeTopics, 'edit' )
    def edit( self, value ):
        """
            Update the value we are to match up against.
        """
        self.value = str( value )

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems( self ):
        """
            Return a sequence of criteria items, used by Topic.buildQuery.
        """
        result = []

        if self.value is not '':
            result.append( ( self.field, self.value ) )

        return tuple( result )

InitializeClass( SimpleStringCriterion )

# Register as a criteria type with the Topic class
Topic._criteriaTypes.append( SimpleStringCriterion )
