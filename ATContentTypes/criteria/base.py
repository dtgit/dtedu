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

__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from Products.Archetypes.atapi import BaseContentMixin

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.Archetypes.ClassGen import generateClass
from Products.ATContentTypes.interfaces import IATTopicCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from Products.CMFCore.PortalContent import PortalContent
from Products.Archetypes.interfaces.base import IBaseContent

class NonRefCatalogContent(BaseContentMixin):
    """Base class for content that is neither referenceable nor in the catalog
    """

    isReferenceable = None

    __implements__ = (PortalContent.__implements__, IATTopicCriterion,
                      IBaseContent)

    # reference register / unregister methods
    def _register(self, *args, **kwargs): pass
    def _unregister(self, *args, **kwargs): pass
    def _updateCatalog(self, *args, **kwargs): pass
    def _referenceApply(self, *args, **kwargs): pass
    def _uncatalogUID(self, *args, **kwargs): pass
    def _uncatalogRefs(self, *args, **kwargs): pass

    # catalog methods
    def indexObject(self, *args, **kwargs): pass
    def unindexObject(self, *args, **kwargs): pass
    def reindexObject(self, *args, **kwargs): pass

class ATBaseCriterion(NonRefCatalogContent):
    """A basic criterion"""

    security = ClassSecurityInfo()

    __implements__ = (IATTopicCriterion, NonRefCatalogContent.__implements__)

    schema = ATBaseCriterionSchema
    meta_type = 'ATBaseCriterion'
    archetype_name = 'Base Criterion'

    def __init__(self, id=None, field=None, oid=None):
        if oid is not None:
            if field is None:
                field = id
            id = oid
        assert id
        NonRefCatalogContent.__init__(self, id)
        self.getField('id').set(self, id)
        self.getField('field').set(self, field)

    security.declareProtected(View, 'getId')
    def getId(self):
        """Get the object id"""
        return str(self.id)

    def setId(self, value, *kw):
        """Setting a new ID isn't allowed
        """
        assert value == self.getId(), 'You are not allowed to change the id'

    security.declareProtected(View, 'Type')
    def Type(self):
        return self.archetype_name

    security.declareProtected(View, 'Description')
    def Description(self):
        lines = [ line.strip() for line in self.__doc__.splitlines() ]
        return ' '.join( [ line for line in lines if line ] )

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        """Return a sequence of items to be used to build the catalog query.
        """
        return ()

# because I don't register the class I've to generator it on my own. Otherwise
# I'm not able to unit test it in the right way.
generateClass(ATBaseCriterion)
InitializeClass(ATBaseCriterion)
