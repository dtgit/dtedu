#
# Tests the PloneTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from AccessControl import getSecurityManager
from Acquisition import aq_base

PloneTestCase.setupPloneSite()
default_user = PloneTestCase.default_user

if PloneTestCase.PLONE25:
    PREFIX = ''
else:
    PREFIX = 'group_'

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestPloneTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0

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

    def testSetRoles(self):
        self.setRoles(['Manager'])
        acl_user = self.portal.acl_users.getUserById(default_user)
        self.assertEqual(sortTuple(acl_user.getRoles()), ('Authenticated', 'Manager'))

    def testSetRolesUser2(self):
        self.membership.addMember('user2', 'secret', ['Member'], [])
        self.setRoles(['Manager'], 'user2')
        acl_user = self.portal.acl_users.getUserById('user2')
        self.assertEqual(sortTuple(acl_user.getRoles()), ('Authenticated', 'Manager'))

    def testSetRolesAuthUser(self):
        self.setRoles(['Manager'])
        auth_user = getSecurityManager().getUser()
        self.assertEqual(sortTuple(auth_user.getRoles()), ('Authenticated', 'Manager'))

    if PloneTestCase.PLONE30:

        def testSetGroups(self):
            self.groups.addGroup('Editors', [], [])
            self.setGroups(['Editors'])
            acl_user = self.portal.acl_users.getUserById(default_user)
                                                              # Auto group
            self.assertEqual(sortTuple(acl_user.getGroups()), ('AuthenticatedUsers', 'Editors'))
            self.assertEqual(sortTuple(acl_user.getRoles()), ('Authenticated', 'Member'))

        def testSetGroupsUser2(self):
            self.membership.addMember('user2', 'secret', ['Member'], [])
            self.groups.addGroup('Editors', [], [])
            self.setGroups(['Editors'], 'user2')
            acl_user = self.portal.acl_users.getUserById('user2')
                                                              # Auto group
            self.assertEqual(sortTuple(acl_user.getGroups()), ('AuthenticatedUsers', 'Editors'))
            self.assertEqual(sortTuple(acl_user.getRoles()), ('Authenticated', 'Member'))

        def testSetGroupsAuthUser(self):
            self.groups.addGroup('Editors', [], [])
            self.setGroups(['Editors'])
            auth_user = getSecurityManager().getUser()
                                                               # Auto group
            self.assertEqual(sortTuple(auth_user.getGroups()), ('AuthenticatedUsers', 'Editors'))
            self.assertEqual(sortTuple(auth_user.getRoles()), ('Authenticated', 'Member'))

    else:

        def testSetGroups(self):
            self.groups.addGroup('Editors', [], [])
            self.setGroups(['Editors'])
            acl_user = self.portal.acl_users.getUserById(default_user)
            self.assertEqual(sortTuple(acl_user.getGroups()), (PREFIX+'Editors',))
            self.assertEqual(sortTuple(acl_user.getRoles()), ('Authenticated', 'Member'))

        def testSetGroupsUser2(self):
            self.membership.addMember('user2', 'secret', ['Member'], [])
            self.groups.addGroup('Editors', [], [])
            self.setGroups(['Editors'], 'user2')
            acl_user = self.portal.acl_users.getUserById('user2')
            self.assertEqual(sortTuple(acl_user.getGroups()), (PREFIX+'Editors',))
            self.assertEqual(sortTuple(acl_user.getRoles()), ('Authenticated', 'Member'))

        def testSetGroupsAuthUser(self):
            self.groups.addGroup('Editors', [], [])
            self.setGroups(['Editors'])
            auth_user = getSecurityManager().getUser()
            self.assertEqual(sortTuple(auth_user.getGroups()), (PREFIX+'Editors',))
            self.assertEqual(sortTuple(auth_user.getRoles()), ('Authenticated', 'Member'))

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

    if PloneTestCase.PLONE30:

        def testGetSite(self):
            from zope.app.component.hooks import getSite
            self.failUnless(aq_base(getSite()) is aq_base(self.portal))


class TestVersionConstants(PloneTestCase.PloneTestCase):

    def testConstants(self):
        if PloneTestCase.PLONE25:
            self.failUnless(PloneTestCase.PLONE21)
        if PloneTestCase.PLONE30:
            self.failUnless(PloneTestCase.PLONE25)
            self.failUnless(PloneTestCase.PLONE21)
        if PloneTestCase.PLONE31:
            self.failUnless(PloneTestCase.PLONE30)
            self.failUnless(PloneTestCase.PLONE25)
            self.failUnless(PloneTestCase.PLONE21)
        if PloneTestCase.PLONE40:
            self.failUnless(PloneTestCase.PLONE31)
            self.failUnless(PloneTestCase.PLONE30)
            self.failUnless(PloneTestCase.PLONE25)
            self.failUnless(PloneTestCase.PLONE21)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneTestCase))
    suite.addTest(makeSuite(TestVersionConstants))
    return suite

if __name__ == '__main__':
    framework()

