#
# Tests a CMF Document
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFTestCase import CMFTestCase
from Acquisition import aq_base

CMFTestCase.setupCMFSite()


class TestDocument(CMFTestCase.CMFTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.folder.invokeFactory('Document', id='doc')

    def testAddDocument(self):
        self.failUnless(hasattr(aq_base(self.folder), 'doc'))
        self.failUnless(self.catalog(getId='doc'))

    def testEditDocument(self):
        self.folder.doc.edit(text_format='plain', text='data')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')

    def testReindexDocument(self):
        self.assertEqual(len(self.catalog(getId='doc', Title='Foo')), 0)
        self.folder.doc.setTitle('Foo')
        self.folder.doc.reindexObject()
        self.assertEqual(len(self.catalog(getId='doc', Title='Foo')), 1)

    def testDeleteDocument(self):
        self.assertEqual(len(self.catalog(getId='doc')), 1)
        self.folder._delObject('doc')
        self.assertEqual(len(self.catalog(getId='doc')), 0)

    def testSubmitDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'pending')
        self.assertEqual(len(self.catalog(getId='doc', review_state='pending')), 1)

    def testRejectDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.setRoles(['Reviewer'])
        self.workflow.doActionFor(self.folder.doc, 'reject')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'private')
        self.assertEqual(len(self.catalog(getId='doc', review_state='private')), 1)

    def testAcceptDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.setRoles(['Reviewer'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'published')
        self.assertEqual(len(self.catalog(getId='doc', review_state='published')), 1)

    def testPublishDocument(self):
        self.setRoles(['Reviewer'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'published')
        self.assertEqual(len(self.catalog(getId='doc', review_state='published')), 1)

    def testRetractDocument(self):
        self.setRoles(['Reviewer'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.workflow.doActionFor(self.folder.doc, 'retract')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'private')
        self.assertEqual(len(self.catalog(getId='doc', review_state='private')), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDocument))
    return suite

if __name__ == '__main__':
    framework()

