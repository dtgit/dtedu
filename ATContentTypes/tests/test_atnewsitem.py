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

__author__ = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

import time, transaction
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.atapi import *
from Products.ATContentTypes.tests.utils import dcEdit

from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.ATContentTypes.tests.utils import NotRequiredTidyHTMLValidator
from Products.ATContentTypes.interfaces import ITextContent
from Products.ATContentTypes.interfaces import IImageContent
from Products.ATContentTypes.interfaces import IATNewsItem
from Interface.Verify import verifyObject

# z3 imports
from Products.ATContentTypes.interface import ITextContent as Z3ITextContent
from Products.ATContentTypes.interface import IImageContent as Z3IImageContent
from Products.ATContentTypes.interface import IATNewsItem as Z3IATNewsItem
from zope.interface.verify import verifyObject as Z3verifyObject


tests = []

TEXT = "lorum ipsum"

def editATCT(obj):
    dcEdit(obj)
    obj.setText(TEXT)

class TestSiteATNewsItem(atcttestcase.ATCTTypeTestCase):

    klass = ATNewsItem
    portal_type = 'News Item'
    title = 'News Item'
    meta_type = 'ATNewsItem'
    icon = 'newsitem_icon.gif'

    def test_implementsTextContent(self):
        iface = ITextContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3TextContent(self):
        iface = Z3ITextContent
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsImageContent(self):
        iface = IImageContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3ImageContent(self):
        iface = Z3IImageContent
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsATNewsItem(self):
        iface = IATNewsItem
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3ATNewsItem(self):
        iface = Z3IATNewsItem
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_edit(self):
        new = self._ATCT
        editATCT(new)

    def test_get_size(self):
        atct = self._ATCT
        editATCT(atct)
        self.failUnlessEqual(atct.get_size(), len(TEXT))

tests.append(TestSiteATNewsItem)

class TestATNewsItemFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATNewsItem)

    def test_textField(self):
        dummy = self._dummy
        field = dummy.getField('text')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getText',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setText',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'text', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == NotRequiredTidyHTMLValidator,
                        'Value is %s' % repr(field.validators))
        self.failUnless(isinstance(field.widget, RichWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)
        self.failUnless(field.default_content_type is None,
                        'Value is %s' % field.default_content_type)
        self.failUnless(field.default_output_type == 'text/x-html-safe',
                        'Value is %s' % field.default_output_type)
        self.failUnless('text/html' in field.getAllowedContentTypes(dummy))

tests.append(TestATNewsItemFields)

class TestATNewsItemFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'News Item'
    views = ('newsitem_view', )

tests.append(TestATNewsItemFunctional)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
