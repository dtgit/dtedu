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

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.lib.validators import TidyHtmlWithCleanupValidator
from Products.ATContentTypes.tests.utils import NotRequiredTidyHTMLValidator
from Products.ATContentTypes.tests.utils import input_file_path
from Products.ATContentTypes.interfaces import IHistoryAware
from Products.ATContentTypes.interfaces import ITextContent
from Products.ATContentTypes.interfaces import IATDocument
from Interface.Verify import verifyObject
from cgi import FieldStorage
from Products.ATContentTypes import config as atct_config
from ZPublisher.HTTPRequest import FileUpload

# z3 imports
from Products.ATContentTypes.interface import IHistoryAware as Z3IHistoryAware
from Products.ATContentTypes.interface import ITextContent as Z3TextContent
from Products.ATContentTypes.interface import IATDocument as Z3IATDocument
from zope.interface.verify import verifyObject as Z3verifyObject

example_stx = """
Header

 Text, Text, Text

   * List
   * List
"""

example_rest = """
Header
======

Text, text, text

* List
* List
"""

def editATCT(obj):
    text_format='text/structured'
    dcEdit(obj)
    obj.setText(example_stx, mimetype = text_format)

tests = []

class TestSiteATDocument(atcttestcase.ATCTTypeTestCase):

    klass = ATDocument
    portal_type = 'Document'
    title = 'Page'
    meta_type = 'ATDocument'
    icon = 'document_icon.gif'

    def test_doesImplementHistoryAware(self):
        iface = IHistoryAware
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_doesImplementZ3HistoryAware(self):
        iface = Z3IHistoryAware
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsTextContent(self):
        iface = ITextContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3TextContent(self):
        iface = Z3TextContent
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsATDocument(self):
        iface = IATDocument
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_implementsZ3ATDocument(self):
        iface = Z3IATDocument
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_edit(self):
        new = self._ATCT
        editATCT(new)

    def test_cmf_edit_failure(self):
        self._ATCT.edit(thisisnotcmfandshouldbeignored=1)

    def test_rename_keeps_contenttype(self):
        doc = self._ATCT
        doc.setText(example_rest, mimetype="text/x-rst")
        self.failUnless(str(doc.getField('text').getContentType(doc)) == "text/x-rst")
        #make sure we have _p_jar
        transaction.savepoint(optimistic=True)

        cur_id = 'ATCT'
        new_id = 'WasATCT'
        self.folder.manage_renameObject(cur_id, new_id)
        doc = getattr(self.folder, new_id)
        field = doc.getField('text')
        self.failUnless(str(field.getContentType(doc)) == "text/x-rst")

    def test_x_safe_html(self):
        doc = self._ATCT
        mimetypes = (
            ('text/html', '<p>test</p>'),
            # MTR doens't know about text/stx, and transforming
            # doubles the tags. Yuck.
            ('text/structured', '<p><p>test</p></p>\n'),
            # XXX
            # ('text/x-rst', ("<p>&lt;p&gt;test&lt;/p&gt;&lt;script&gt;"
            #                 "I'm a nasty boy&lt;p&gt;nested&lt;/p&gt;"
            #                 "&lt;/script&gt;</p>\n")),
            # ('text/python-source', '<p>test</p>'),
            # XXX
            # ('text/plain', ("<p>&lt;p&gt;test&lt;/p&gt;&lt;script&gt;"
            #                 "I'm a nasty boy&lt;p&gt;nested&lt;/p&gt;"
            #                 "&lt;/script&gt;</p>\n")),
            )
        for mimetype, expected in mimetypes:
            # scrub html is removing unallowed tags
            text = "<p>test</p><script>I'm a nasty boy<p>nested</p></script>"
            doc.setText(text, mimetype=mimetype)
            txt = doc.getText()
            self.failUnlessEqual(txt, expected, (txt, expected, mimetype))

    def test_get_size(self):
        atct = self._ATCT
        editATCT(atct)
        self.failUnlessEqual(atct.get_size(), len(example_stx))

    if atct_config.HAS_MX_TIDY:
        # this test is null and void if mx.Tidy isn't even installed

        def test_tidy_validator_with_upload_wrong_encoding(self): 
            doc = self._ATCT
    
            field = doc.getField('text')
            request = self.app.REQUEST
            setattr(request, 'text_text_format', 'text/html')
            input_file_name = 'tidy1-in.html'
            in_file = open(input_file_path(input_file_name))
            env = {'REQUEST_METHOD':'PUT'}
            headers = {'content-type':'text/html',
                       'content-length': len(in_file.read()),
                       'content-disposition':'attachment; filename=%s' % input_file_name}
            in_file.seek(0)
            fs = FieldStorage(fp=in_file, environ=env, headers=headers)
            f = FileUpload(fs)
    
            tcv = TidyHtmlWithCleanupValidator('tidy_validator_with_cleanup')
            result = tcv.__call__(f, field=field, REQUEST=request)
    
            self.assertEquals(result, 1)
    
            expected_file = open(input_file_path('tidy1-out.html'))
            expected = expected_file.read()
            expected_file.close()
            self.assertEquals(request['text_tidier_data'], expected)
        
tests.append(TestSiteATDocument)

class TestATDocumentFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATDocument)

    def test_text_field_mutator_filename(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', filename='foo.txt')
        self.assertEquals(field.getFilename(dummy), 'foo.txt')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

    def test_text_field_mutator_mime(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', mimetype='text/plain')
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

    def test_text_field_mutator_none_mime(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', mimetype=None)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

    def test_text_field_mutator_none_filename(self):
        dummy = self._dummy
        field = dummy.getField('text')
        mutator = field.getMutator(dummy)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/html')
        mutator('', filename=None)
        self.assertEquals(field.getFilename(dummy), '')
        self.assertEquals(field.getContentType(dummy), 'text/plain')

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

tests.append(TestATDocumentFields)

class TestATDocumentFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'Document'
    views = ('document_view', )

    def test_id_change_on_initial_edit(self):
        """Make sure Id is taken from title on initial edit and not otherwise"""
        # first create an object using the createObject script

        response = self.publish(self.folder_path +
                                '/createObject?type_name=%s' % self.portal_type,
                                self.basic_auth)

        self.assertStatusEqual(response.getStatus(), 302) # Redirect to edit

        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.folder_url), location)
        self.failUnless(location.endswith('edit'), location)

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK

        #Change the title
        temp_id = location.split('/')[-2]
        obj_title = "New Title for Object"
        new_id = "new-title-for-object"
        new_obj = getattr(self.folder.aq_explicit, temp_id)
        new_obj_path = '/%s' % new_obj.absolute_url(1)
        self.failUnlessEqual(new_obj.checkCreationFlag(), True) # object is not yet edited

        response = self.publish('%s/atct_edit?form.submitted=1&title=%s&text=Blank' % (new_obj_path, obj_title,), self.basic_auth) # Edit object
        self.assertStatusEqual(response.getStatus(), 302) # OK
        self.failUnlessEqual(new_obj.getId(), new_id) # does id match
        self.failUnlessEqual(new_obj.checkCreationFlag(), False) # object is fully created
        new_title = "Second Title"
        response = self.publish('%s/atct_edit?form.submitted=1&title=%s&text=Blank' % ('/%s' % new_obj.absolute_url(1), new_title,), self.basic_auth) # Edit object
        self.assertStatusEqual(response.getStatus(), 302) # OK
        self.failUnlessEqual(new_obj.getId(), new_id) # id shouldn't have changed

tests.append(TestATDocumentFunctional)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
