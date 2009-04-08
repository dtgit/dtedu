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

import os, sys
import transaction
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

from cStringIO import StringIO
from OFS.Image import Image as OFSImage

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.atapi import *
from Products.ATContentTypes.tests.utils import dcEdit, PACKAGE_HOME

from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.interfaces import IImageContent
from Products.ATContentTypes.interfaces import IATImage

from Interface.Verify import verifyObject

# z3 imports
from Products.ATContentTypes.interface import IATImage as Z3IATImage
from Products.ATContentTypes.interface import IImageContent as Z3IImageContent
from zope.interface.verify import verifyObject as Z3verifyObject

# third party extension
import exif

def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = os.path.join(PACKAGE_HOME, 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data

TEST_EXIF_ERROR = loadImage('canoneye.jpg')
TEST_GIF = loadImage('test.gif')
TEST_GIF_LEN = len(TEST_GIF)
TEST_DIV_ERROR = loadImage('divisionerror.jpg')
TEST_JPEG_FILE = open(os.path.join(PACKAGE_HOME, 'input', 'canoneye.jpg'), 'rb')
# XXX replace it by an image with exif informations but w/o
# the nasty error ...
TEST_JPEG = loadImage('canoneye.jpg')
TEST_JPEG_LEN = len(TEST_JPEG)

def editATCT(obj):
    obj.setImage(TEST_GIF, content_type="image/gif")
    dcEdit(obj)

tests = []

class TestSiteATImage(atcttestcase.ATCTTypeTestCase):

    klass = ATImage
    portal_type = 'Image'
    title = 'Image'
    meta_type = 'ATImage'
    icon = 'image_icon.gif'

    def test_implementsImageContent(self):
        iface = IImageContent
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_z3ImplementsImageContent(self):
        iface = Z3IImageContent
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_implementsATImage(self):
        iface = IATImage
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_z3ImplementsImageContent(self):
        iface = Z3IATImage
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_edit(self):
        new = self._ATCT
        editATCT(new)

    def test_getEXIF(self):
        # NOTE: not a real test
        exif_data = self._ATCT.getEXIF()
        self.failUnless(isinstance(exif_data, dict), type(exif_data))

    def test_exifOrientation(self):
        # NOTE: not a real test
        r, m = self._ATCT.getEXIFOrientation()

    def test_transform(self):
        # NOTE: not a real test
        self._ATCT.transformImage(2)

    def test_autotransform(self):
        # NOTE: not a real test
        self._ATCT.autoTransformImage()

    def test_broken_pil(self):
        # PIL has a nasty bug when the image ratio is too extrem like 300x15:
        # Module PIL.Image, line 1136, in save
        # Module PIL.PngImagePlugin, line 510, in _save
        # Module PIL.ImageFile, line 474, in _save
        # SystemError: tile cannot extend outside image
        atct = self._ATCT

        # test upload
        atct.setImage(TEST_GIF, mimetype='image/gif', filename='test.gif')
        self.failUnlessEqual(atct.getImage().data, TEST_GIF)

    def test_bobo_hook(self):
        atct = self._ATCT
        REQUEST = {'method' : 'GET'}
        scales = atct.getField('image').getAvailableSizes(atct)
        atct.setImage(TEST_GIF, mimetype='image/gif', filename='test.gif')

        img = atct.__bobo_traverse__(REQUEST, 'image')
        self.failUnless(isinstance(img, OFSImage), img)

        # test if all scales exist
        for scale in scales.keys():
            name = 'image_' + scale
            img = atct.__bobo_traverse__(REQUEST, name)
            self.failUnless(isinstance(img, OFSImage), img)

    def test_division_by_0_pil(self):
        # pil generates a division by zero error on some images
        atct = self._ATCT

        # test upload
        atct.setImage(TEST_DIV_ERROR, mimetype='image/jpeg',
                      filename='divisionerror.jpg')
        self.failUnlessEqual(atct.getImage().data, TEST_DIV_ERROR)


    def test_get_size(self):
        atct = self._ATCT
        editATCT(atct)
        self.failUnlessEqual(len(TEST_GIF), TEST_GIF_LEN)
        self.failUnlessEqual(atct.get_size(), TEST_GIF_LEN)

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

    def test_dcEdit(self):
        new = self._ATCT
        new.setImage(TEST_GIF, content_type="image/gif")
        dcEdit(new)

    def test_broken_exif(self):
        # This test fails even with the 2005.05.12 exif version from
        #    http://home.cfl.rr.com/genecash/
        f = StringIO(TEST_EXIF_ERROR)
        exif_data = exif.process_file(f, debug=False)
        # probably want to add some tests on returned data. Currently gives
        #  ValueError in process_file

    def test_exif_upload(self):
        atct = self._ATCT
        atct._image_exif = None

        # string upload
        atct.setImage(TEST_JPEG)
        self.failUnless(len(atct.getEXIF()), atct.getEXIF())
        atct._image_exif = None

        # file upload
        atct.setImage(TEST_JPEG_FILE)
        self.failUnless(len(atct.getEXIF()), atct.getEXIF())
        atct._image_exif = None

        # Pdata upload
        from OFS.Image import Pdata
        pd = Pdata(TEST_JPEG)
        atct.setImage(pd)
        self.failUnless(len(atct.getEXIF()), atct.getEXIF())
        atct._image_exif = None

        # ofs image upload
        ofs = atct.getImage()
        atct.setImage(ofs)
        self.failUnless(len(atct.getEXIF()), atct.getEXIF())
        atct._image_exif = None

tests.append(TestSiteATImage)

class TestATImageFields(atcttestcase.ATCTFieldTestCase):

    # Title is not a required field, since we don't require them 
    # on File/Image - they are taken from the filename if not present.
    # "Add the comment 'damn stupid fucking test'" -- optilude ;)
    def test_title(self):
        pass

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATImage)

    def test_imageField(self):
        dummy = self._dummy
        field = dummy.getField('image')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getImage',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setImage',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'image', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.validators == "(('isNonEmptyFile', V_REQUIRED), ('checkImageMaxSize', V_REQUIRED))",
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, ImageWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))
        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)

tests.append(TestATImageFields)

class TestATImageFunctional(atctftestcase.ATCTIntegrationTestCase):
    
    portal_type = 'Image'
    views = ('image_view', 'download', 'atct_image_transform')

    def afterSetUp(self):
        atctftestcase.ATCTIntegrationTestCase.afterSetUp(self)
        self.obj.setImage(TEST_GIF, content_type="image/gif")
        dcEdit(self.obj)

    def test_url_returns_image(self):
        response = self.publish(self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) # OK
        
    def test_bobo_hook_security(self):
        # Make sure that users with 'View' permission can use the
        # bobo_traversed image scales, even if denied to anonymous
        response1 = self.publish(self.obj_path+'/image', self.basic_auth)
        self.assertStatusEqual(response1.getStatus(), 200) # OK
        # deny access to anonymous
        self.obj.manage_permission('View', ['Manager','Member'],0)
        response2 = self.publish(self.obj_path+'/image', self.basic_auth)
        # Should be allowed for member
        self.assertStatusEqual(response2.getStatus(), 200) # OK
        # Should fail for anonymous
        self.error_log._ignored_exceptions = ('Unauthorized', )
        response3 = self.publish(self.obj_path+'/image')
        self.assertStatusEqual(response3.getStatus(), 401)

tests.append(TestATImageFunctional)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
