#
# Tests the CMFTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFTestCase import CMFTestCase
from Acquisition import aq_base

CMFTestCase.setupCMFSite()
default_user = CMFTestCase.default_user


class TestCMFTestCase(CMFTestCase.CMFTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

    def testDefaultMemberarea(self):
        self.assertEqual(self.folder.getOwner().getId(), default_user)
        self.assertEqual(self.folder.get_local_roles_for_userid(default_user), ('Owner',))
        self.failIf('index_html' in self.folder.objectIds())

    def testCreateMemberarea(self):
        self.membership.addMember('user2', 'secret', [], [])
        self.createMemberarea('user2')
        home = self.membership.getHomeFolder('user2')
        self.assertEqual(home.getOwner().getId(), 'user2')
        self.assertEqual(home.get_local_roles_for_userid('user2'), ('Owner',))
        self.assertEqual(home.get_local_roles_for_userid(default_user), ())
        self.failIf('index_html' in home.objectIds())

    def testAddDocument(self):
        self.folder.invokeFactory('Document', id='doc')
        self.failUnless('doc' in self.folder.objectIds())

    def testEditDocument(self):
        self.folder.invokeFactory('Document', id='doc')
        self.folder.doc.edit(text_format='plain', text='data')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')

    def testPublishDocument(self):
        self.folder.invokeFactory('Document', id='doc')
        self.setRoles(['Reviewer'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        review_state = self.workflow.getInfoFor(self.folder.doc, 'review_state')
        self.assertEqual(review_state, 'published')
        self.assertEqual(len(self.catalog(getId='doc', review_state='published')), 1)

    def testSkinScript(self):
        self.folder.invokeFactory('Document', id='doc', title='Foo')
        self.assertEqual(self.folder.doc.TitleOrId(), 'Foo')

    if CMFTestCase.CMF21:

        def testGetSite(self):
            from zope.app.component.hooks import getSite
            self.failUnless(aq_base(getSite()) is aq_base(self.portal))


class TestVersionConstants(CMFTestCase.CMFTestCase):

    def testConstants(self):
        if CMFTestCase.CMF16:
            self.failUnless(CMFTestCase.CMF15)
        if CMFTestCase.CMF20:
            self.failUnless(CMFTestCase.CMF16)
            self.failUnless(CMFTestCase.CMF15)
        if CMFTestCase.CMF21:
            self.failUnless(CMFTestCase.CMF20)
            self.failUnless(CMFTestCase.CMF16)
            self.failUnless(CMFTestCase.CMF15)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCMFTestCase))
    suite.addTest(makeSuite(TestVersionConstants))
    return suite

if __name__ == '__main__':
    framework()

