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
"""Tests for module aliases from old .types to new .content

Tests if the classes can be imported from the old path but the new path is the right
path for pickling.
"""

__author__ = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

tests = []

class TestModuleAliases(atcttestcase.ATCTSiteTestCase):

    def test_import_content_type(self):
        from Products.ATContentTypes.types.ATDocument import ATDocument
        from Products.ATContentTypes.types.ATEvent import ATEvent
        from Products.ATContentTypes.types.ATFavorite import ATFavorite
        from Products.ATContentTypes.types.ATFile import ATFile
        from Products.ATContentTypes.types.ATFolder import ATFolder
        from Products.ATContentTypes.types.ATFolder import ATBTreeFolder
        from Products.ATContentTypes.types.ATImage import ATImage
        from Products.ATContentTypes.types.ATLink import ATLink
        from Products.ATContentTypes.types.ATNewsItem import ATNewsItem
        from Products.ATContentTypes.types.ATTopic import ATTopic

        self.failUnlessEqual(ATDocument.__module__,
            'Products.ATContentTypes.content.document')
        self.failUnlessEqual(ATEvent.__module__,
            'Products.ATContentTypes.content.event')
        self.failUnlessEqual(ATFavorite.__module__,
            'Products.ATContentTypes.content.favorite')
        self.failUnlessEqual(ATFile.__module__,
            'Products.ATContentTypes.content.file')
        self.failUnlessEqual(ATFolder.__module__,
            'Products.ATContentTypes.content.folder')
        self.failUnlessEqual(ATBTreeFolder.__module__,
            'Products.ATContentTypes.content.folder')
        self.failUnlessEqual(ATImage.__module__,
            'Products.ATContentTypes.content.image')
        self.failUnlessEqual(ATLink.__module__,
            'Products.ATContentTypes.content.link')
        self.failUnlessEqual(ATNewsItem.__module__,
            'Products.ATContentTypes.content.newsitem')
        self.failUnlessEqual(ATTopic.__module__,
            'Products.ATContentTypes.content.topic')

    def test_import_criteria(self):
        from Products.ATContentTypes.criteria.boolean import \
            ATBooleanCriterion
        from Products.ATContentTypes.criteria.date import \
            ATDateCriteria
        from Products.ATContentTypes.criteria.daterange import \
            ATDateRangeCriterion
        from Products.ATContentTypes.criteria.list import \
            ATListCriterion
        from Products.ATContentTypes.criteria.portaltype import \
            ATPortalTypeCriterion
        from Products.ATContentTypes.criteria.reference import \
            ATReferenceCriterion
        from Products.ATContentTypes.criteria.selection import \
            ATSelectionCriterion
        from Products.ATContentTypes.criteria.simpleint import \
            ATSimpleIntCriterion
        from Products.ATContentTypes.criteria.simplestring import \
            ATSimpleStringCriterion
        from Products.ATContentTypes.criteria.sort import \
            ATSortCriterion

        self.failUnlessEqual(ATBooleanCriterion.__module__,
            'Products.ATContentTypes.criteria.boolean')
        self.failUnlessEqual(ATDateCriteria.__module__,
            'Products.ATContentTypes.criteria.date')
        self.failUnlessEqual(ATDateRangeCriterion.__module__,
            'Products.ATContentTypes.criteria.daterange')
        self.failUnlessEqual(ATListCriterion.__module__,
            'Products.ATContentTypes.criteria.list')
        self.failUnlessEqual(ATPortalTypeCriterion.__module__,
            'Products.ATContentTypes.criteria.portaltype')
        self.failUnlessEqual(ATReferenceCriterion.__module__,
            'Products.ATContentTypes.criteria.reference')
        self.failUnlessEqual(ATSelectionCriterion.__module__,
            'Products.ATContentTypes.criteria.selection')
        self.failUnlessEqual(ATSimpleIntCriterion.__module__,
            'Products.ATContentTypes.criteria.simpleint')
        self.failUnlessEqual(ATSimpleStringCriterion.__module__,
            'Products.ATContentTypes.criteria.simplestring')
        self.failUnlessEqual(ATSortCriterion.__module__,
            'Products.ATContentTypes.criteria.sort')

    def test_import_z3_interfaces(self):
        # People import things in different ways, let's make sure they all
        # work (doing so actually requires more than just an alias
        from Products.ATContentTypes.z3.interfaces import ITextContent
        from Products.ATContentTypes.z3 import interfaces
        from Products.ATContentTypes import z3

        self.failUnlessEqual(ITextContent.__module__,
            'Products.ATContentTypes.interface.interfaces')
        self.failUnlessEqual(interfaces.ITextContent.__module__,
            'Products.ATContentTypes.interface.interfaces')
        self.failUnlessEqual(z3.interfaces.ITextContent.__module__,
            'Products.ATContentTypes.interface.interfaces')


tests.append(TestModuleAliases)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
