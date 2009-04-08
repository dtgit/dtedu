##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for http://zope.org/Collectors/CMF/318

$Id: test_DiscussionReply.py 73035 2007-03-07 16:41:03Z jens $
"""

import unittest
from Testing import ZopeTestCase

from AccessControl.SecurityManagement import newSecurityManager
from zope.app.component.hooks import setSite

from Products.CMFDefault.testing import FunctionalLayer


class DiscussionReplyTest(ZopeTestCase.FunctionalTestCase):

    layer = FunctionalLayer

    def afterSetUp(self):
        setSite(self.app.site)
        self.portal = self.app.site
        # Become a Manager
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('manager', '', ['Manager'], [])
        self.site_login('manager')
        # Make a document
        self.discussion = self.portal.portal_discussion
        self.portal.invokeFactory('Document', id='doc')
        self.discussion.overrideDiscussionFor(self.portal.doc, 1)
        # Publish it
        self.workflow = self.portal.portal_workflow
        self.workflow.doActionFor(self.portal.doc, 'publish')

    def site_login(self, name):
        user = self.uf.getUserById(name)
        user = user.__of__(self.uf)
        newSecurityManager(None, user)

    def testDiscussionReply(self):
        self.discussion.getDiscussionFor(self.portal.doc)
        self.portal.doc.talkback.createReply('Title', 'Text')
        reply = self.portal.doc.talkback.objectValues()[0]
        self.assertEqual(reply.Title(), 'Title')
        self.assertEqual(reply.EditableBody(), 'Text')


class DiscussionReplyTestMember(DiscussionReplyTest):

    # Run the test again as another Member, i.e. reply to someone
    # else's document.

    def afterSetUp(self):
        DiscussionReplyTest.afterSetUp(self)
        self.uf.userFolderAddUser('member', '', ['Member'], [])
        self.site_login('member')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DiscussionReplyTest))
    suite.addTest(unittest.makeSuite(DiscussionReplyTestMember))
    return suite

if __name__ == '__main__':
    from Products.CMFCore.testing import run
    run(test_suite())
