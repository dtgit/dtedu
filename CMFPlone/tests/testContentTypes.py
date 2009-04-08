#
# Tests the content types
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from zope.i18nmessageid.message import Message

from Acquisition import aq_base
from Products.ATContentTypes.interfaces import IATContentType

AddPortalTopics = 'Add portal topics'

atct_types = ('Document', 'Event', 'Favorite', 'File', 'Folder',
              'Large Plone Folder', 'Image', 'Link', 'News Item',
             )


class TestATContentTypes(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(perms + [AddPortalTopics], 'Member')
        self.types = self.portal.portal_types

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def construct(self, portal_type, id, folder):
        fti = self.types.getTypeInfo(portal_type)
        fti.constructInstance(folder, id=id)
        return getattr(folder, id)

    def createWithoutConstruction(self, portal_type, id, folder):
        fti = self.types.getTypeInfo(portal_type)
        # manual creation
        p = folder.manage_addProduct[fti.product]
        m = getattr(p, fti.factory)
        m(id) # create it
        return folder._getOb(id)

    def testPortalTypeName(self):
        for pt in atct_types:
            ob = self.construct(pt, pt, self.folder)
            self.failUnlessEqual(ob._getPortalTypeName(), pt)
            self.failUnlessEqual(ob.portal_type, pt)
            self.failUnless(IATContentType.isImplementedBy(ob))


class TestContentTypes(PloneTestCase.PloneTestCase):
    # This test mirrors TestContentTypeScripts but calls the API and
    # not the skin scripts.

    def afterSetUp(self):
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(perms + [AddPortalTopics], 'Member')

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def testDocumentEdit(self):
        self.folder.invokeFactory('Document', id='doc')
        self.folder.doc.edit(title='Foo', text='data', text_format='html')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.folder.doc.Format(), 'text/html')
        self.assertEqual(self.folder.doc.Title(), 'Foo')

    def testEventEdit(self):
        self.folder.invokeFactory('Event', id='event')
        self.folder.event.edit(title='Foo',
                               start_date='2003-09-18',
                               end_date='2003-09-19')
        self.assertEqual(self.folder.event.Title(), 'Foo')
        self.assertEqual(self.folder.event.start().ISO(), '2003-09-18 00:00:00')
        self.assertEqual(self.folder.event.end().ISO(), '2003-09-19 00:00:00')

    def testFavoriteEdit(self):
        # Note: link_edit does not traverse to remote_url
        self.folder.invokeFactory('Favorite', id='favorite')
        self.folder.favorite.edit(remote_url='bar/baz.html', title='Foo')
        self.assertEqual(self.folder.favorite.getRemoteUrl(),
                         '%s/bar/baz.html' % self.portal.portal_url())
        self.assertEqual(self.folder.favorite.Title(), 'Foo')

    def testFileEdit(self):
        self.folder.invokeFactory('File', id='file')
        self.folder.file.edit(file=dummy.File())
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageEdit(self):
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.edit(file=dummy.Image())
        self.assertEqual(str(self.folder.image.data), dummy.GIF)

    def testFolderEdit(self):
        self.folder.invokeFactory('Folder', id='folder')
        self.folder.folder.edit(title='Foo', description='Bar')
        self.assertEqual(self.folder.folder.Title(), 'Foo')
        self.assertEqual(self.folder.folder.Description(), 'Bar')
        # Edit a second time
        self.folder.folder.edit(title='Fred', description='BamBam')
        self.assertEqual(self.folder.folder.Title(), 'Fred')
        self.assertEqual(self.folder.folder.Description(), 'BamBam')

    def testLinkEdit(self):
        self.folder.invokeFactory('Link', id='link')
        self.folder.link.edit(remote_url='http://foo.com', title='Foo')
        self.assertEqual(self.folder.link.Title(), 'Foo')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'http://foo.com')

    def testNewsItemEdit(self):
        self.folder.invokeFactory('News Item', id='newsitem')
        self.folder.newsitem.edit(text='data', text_format='html', title='Foo')
        self.assertEqual(self.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.folder.newsitem.Format(), 'text/html')
        self.assertEqual(self.folder.newsitem.Title(), 'Foo')

    def testTopicEdit(self):
        self.folder.invokeFactory('Topic', id='topic')
        self.folder.topic.edit(title='Foo')
        self.assertEqual(self.folder.topic.Title(), 'Foo')


class TestContentTypeInformation(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.types = self.portal.portal_types

    def testTypeTitlesAreMessages(self):
        types = self.types.objectValues()
        for t in types:
            # If the title is empty we get back the id
            if t.title:
                self.failUnless(isinstance(t.Title(), Message))
            self.failUnless(isinstance(t.Description(), Message))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestATContentTypes))
    suite.addTest(makeSuite(TestContentTypes))
    suite.addTest(makeSuite(TestContentTypeInformation))
    return suite
