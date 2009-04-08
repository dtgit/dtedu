# -*- coding: utf-8 -*-
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

import unittest
from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

import time, transaction
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.atapi import *
from Products.ATContentTypes.tests.utils import dcEdit
import StringIO

from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IFileContent
from Interface.Verify import verifyObject

# z3 imports
from Products.ATContentTypes.interface import IATFile as Z3IATFile
from Products.ATContentTypes.interface import IFileContent as Z3IFileContent
from zope.interface.verify import verifyObject as Z3verifyObject


file_text = """
foooooo
"""

def editATCT(obj):
    dcEdit(obj)
    obj.edit(file=file_text)

tests = []

class TestSiteATFile(atcttestcase.ATCTTypeTestCase):

    klass = ATFile
    portal_type = 'File'
    title = 'File'
    meta_type = 'ATFile'
    icon = 'file_icon.gif'

    def test_implementsFileContent(self):
        iface = IFileContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3FileContent(self):
        iface = Z3IFileContent
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsATFile(self):
        iface = IATFile
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3ATFile(self):
        iface = Z3IATFile
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_edit(self):
        new = self._ATCT
        editATCT(new)

    def testCompatibilityFileAccess(self):
        new = self._ATCT
        editATCT(new)
        # test for crappy access ways of CMF :)
        self.failUnlessEqual(str(new), file_text)
        self.failUnlessEqual(new.data, file_text)
        self.failUnlessEqual(str(new.getFile()), file_text)
        self.failUnlessEqual(new.getFile().data, file_text)
        self.failUnlessEqual(new.get_data(), file_text)

    def testCompatibilityContentTypeAccess(self):
        new = self._ATCT
        editATCT(new)
        # TODO: more tests

    def test_schema_marshall(self):
        atct = self._ATCT
        schema = atct.Schema()
        marshall = schema.getLayerImpl('marshall')
        marshallers = [PrimaryFieldMarshaller]
        try:
            from Products.Marshall import ControlledMarshaller
            marshallers.append(ControlledMarshaller)
        except ImportError:
            pass
        self.failUnless(isinstance(marshall, tuple(marshallers)), marshall)

    def testInvokeFactoryWithFileContents(self):
        # test for Plone tracker #4939
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'some-filename'
        id = self.folder.invokeFactory(self.portal_type,
                                       'image.2005-11-18.4066860572',
                                       file=fakefile)
        self.assertEquals(id, fakefile.filename)

    def testUpperCaseFilename(self):
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'Some-filename-With-Uppercase.txt'
        id = 'file.2005-11-18.4066860573'
        self.folder.invokeFactory(self.portal_type, id)
        self.folder[id].setFile(fakefile)
        self.failIf(id in self.folder.objectIds())
        self.failUnless(fakefile.filename in self.folder.objectIds())

    def testUpperCaseFilenameWithFunnyCharacters(self):
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'Zope&Plo?ne .txt'
        id = 'file.2005-11-18.4066860574'
        self.folder.invokeFactory(self.portal_type, id)
        self.folder[id].setFile(fakefile)
        self.failIf(id in self.folder.objectIds())
        self.failUnless('Zope-Plo-ne .txt' in self.folder.objectIds())

    def testWindowsUploadFilename(self):
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'c:\\Windows\\Is\\Worthless\\file.txt'
        id = 'file.2005-11-18.4066860574'
        self.folder.invokeFactory(self.portal_type, id)
        self.folder[id].setFile(fakefile)
        self.failIf(id in self.folder.objectIds())
        self.failIf(fakefile.filename in self.folder.objectIds())
        self.failUnless('file.txt' in self.folder.objectIds())

    def testWindowsDuplicateFiles(self):
        class fakefile(StringIO.StringIO):
            pass
        fakefile = fakefile()
        fakefile.filename = 'c:\\Windows\\Is\\Worthless\\file.txt'
        id = 'file.2005-11-18.4066860574'
        self.folder.invokeFactory(self.portal_type, id)
        self.folder[id].setFile(fakefile)
        self.folder.invokeFactory(self.portal_type, id)
        request = self.folder.REQUEST
        request.form['id'] = id
        request.form['file_file'] = fakefile
        errors = {}
        self.folder[id].post_validate(request, errors)
        self.failUnless(errors.has_key('file'))

tests.append(TestSiteATFile)

class TestATFileFields(atcttestcase.ATCTFieldTestCase):

    # Title is not a required field, since we don't require them 
    # on File/Image - they are taken from the filename if not present.
    # "Add the comment 'damn stupid fucking test'" -- optilude ;)
    def test_title(self):
        pass

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATFile)

    def test_fileField(self):
        dummy = self._dummy
        field = dummy.getField('file')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == True, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getFile',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setFile',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'file', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == "(('isNonEmptyFile', V_REQUIRED), ('checkFileMaxSize', V_REQUIRED))",
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, FileWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)

tests.append(TestATFileFields)

class TestCleanupFilename(atcttestcase.ATCTSiteTestCase):

    def test_cleanup_filename(self):
        self.app.REQUEST.set('HTTP_ACCEPT_LANGUAGE', 'el')
        from Products.ATContentTypes.content.base import cleanupFilename
        text = unicode('Νίκος Τζάνος', 'utf-8')
        self.assertEquals(cleanupFilename(text, request=self.app.REQUEST),
                          'Nikos Tzanos')

tests.append(TestCleanupFilename)

class TestATFileFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'File'
    views = ('file_view', 'download', )

    def test_inlineMimetypes_Office(self):
        # Only PDF and Office docs are shown inline
        self.obj.setFormat('application/msword')
        response = self.publish(self.obj_path)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Disposition'), None)

        self.obj.setFormat('application/x-msexcel')
        response = self.publish(self.obj_path)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Disposition'), None)

        self.obj.setFormat('application/vnd.ms-excel')
        response = self.publish(self.obj_path)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Disposition'), None)

        self.obj.setFormat('application/vnd.ms-powerpoint')
        response = self.publish(self.obj_path)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Disposition'), None)

    def test_inlineMimetypes_PDF(self):
        # Only PDF and Office docs are shown inline
        self.obj.setFormat('application/pdf')
        response = self.publish(self.obj_path)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Disposition'), None)

    def test_inlineMimetypes_Text(self):
        # Only PDF and Office docs are shown inline
        self.obj.setFilename('foo.txt')
        self.obj.setFormat('text/plain')
        response = self.publish(self.obj_path)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Disposition'), 'attachment; filename="foo.txt"')

    def test_inlineMimetypes_Binary(self):
        # Only PDF and Office docs are shown inline
        self.obj.setFilename('foo.exe')
        self.obj.setFormat('application/octet-stream')
        response = self.publish(self.obj_path)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Disposition'), 'attachment; filename="foo.exe"')

tests.append(TestATFileFunctional)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
