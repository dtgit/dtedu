#
# Test portal factory
#

import urlparse
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.permissions import AddPortalContent
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin

from AccessControl import Unauthorized
default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)

ADD_DOC_PERM = 'ATContentTypes: Add Document'


class TestPortalFactory(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('member', 'secret', ['Member'], [])
        self.membership.addMember('manager', 'secret', ['Manager'], [])

    def testTraverse(self):
        temp_doc = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.portal_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')

    def testTraverseTwiceByDifferentContentTypes(self):
        temp_doc = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.portal_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')
        temp_img = self.folder.restrictedTraverse('portal_factory/Image/tmp_id_image')
        self.assertEqual(temp_img.portal_type, 'Image')
        self.assertEqual(temp_img.getId(), 'tmp_id_image')

    def testTempFolderLocalRoles(self):
        # Temporary objects should "inherit" local roles from container
        member = self.membership.getMemberById('member')
        self.portal.acl_users.addRole('Foo')

        self.folder.manage_addLocalRoles('member', ('Foo',))
        self.folder.invokeFactory('Folder', id='folder2')
        self.folder.folder2.manage_addLocalRoles('member', ('Reviewer',))

        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object2 = self.folder.folder2.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object2)),
                         ('Authenticated', 'Foo', 'Member', 'Reviewer'))

    def testTempFolderLocalRolesWithBlocking(self):
        # Temporary objects should "inherit" local roles from container,
        # but also need to respect PLIP 16 local role blocking
        member = self.membership.getMemberById('member')
        self.portal.acl_users.addRole('Foo')

        self.folder.manage_addLocalRoles('member', ('Foo',))
        self.folder.invokeFactory('Folder', id='folder2')
        self.folder.folder2.manage_addLocalRoles('member', ('Reviewer',))
        # make folder2 not inherit local roles
        self.portal.plone_utils.acquireLocalRoles(self.folder.folder2, status=0)

        self.assertEqual(sortTuple(member.getRolesInContext(self.folder.folder2)),
                         ('Authenticated', 'Member', 'Reviewer'))

        temp_object2 = self.folder.folder2.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object2)),
                         ('Authenticated', 'Member', 'Reviewer'))

    def testTempFolderPermissionAq(self):
        from Products.CMFPlone.FactoryTool import FACTORY_INFO
        # Temporary folder should acquire same permissions as the intended parent
        self.login('manager')
        self.portal.invokeFactory('Folder', id='folder1')
        folder1 = self.portal.folder1
        folder1.invokeFactory('Folder', id='folder2')
        folder2 = folder1.folder2
        folder2.invokeFactory('Folder', id='folder3')
        folder3 = folder1.folder2.folder3
        folder3.restrictedTraverse('portal_factory/Document/tmp_id')
        # clear out the cached factory info (this would happen by itself in an actual request)
        self.portal.REQUEST.set(FACTORY_INFO, {})

        # make sure no permission is available initially
        self.login('member')
        pm = self.portal.portal_membership
        assert (not pm.checkPermission(ADD_DOC_PERM, folder3))
        self.assertRaises(Unauthorized, folder3.restrictedTraverse, 'portal_factory/Document/tmp_id/atct_edit')
        # clear out the cached factory info (this would happen by itself in an actual request)
        self.portal.REQUEST.set(FACTORY_INFO, {})

        # grant the add permission on the parent
        self.login('manager')
        folder3.manage_permission(ADD_DOC_PERM, ['Authenticated'], 1)

        # now make sure we can see it
        self.login('member')
        assert (pm.checkPermission(ADD_DOC_PERM, folder3))
        #folder3.setConstrainTypesMode(0)
        folder3.restrictedTraverse('portal_factory/Document/tmp_id/atct_edit')
        # clear out the cached factory info (this would happen by itself in an actual request)
        self.portal.REQUEST.set(FACTORY_INFO, {})

        # blow away folder3 and start again
        self.login('manager')
        folder2.manage_delObjects(['folder3'])
        folder2.invokeFactory('Folder', id='folder3')
        folder3 = folder1.folder2.folder3

        # grant the add permission on the grandparent
        folder2.manage_permission(ADD_DOC_PERM, ['Authenticated'], 1)

        # now make sure we can see it
        self.login('member')
        assert (pm.checkPermission(ADD_DOC_PERM, folder3))
        folder3.restrictedTraverse('portal_factory/Document/tmp_id')
        # clear out the cached factory info (this would happen by itself in an actual request)
        self.portal.REQUEST.set(FACTORY_INFO, {})

        # blow away folder2 and start again
        self.login('manager')
        folder1.manage_delObjects(['folder2'])
        folder1.invokeFactory('Folder', id='folder2')
        folder2 = folder1.folder2
        folder2.invokeFactory('Folder', id='folder3')
        folder3 = folder1.folder2.folder3

        # add the permission on the portal root
        self.portal.manage_permission(ADD_DOC_PERM, ['Authenticated'], 1)

        # now make sure we can see it
        self.login('member')
        assert (pm.checkPermission(ADD_DOC_PERM, folder3))
        folder3.restrictedTraverse('portal_factory/Document/tmp_id')
        # clear out the cached factory info (this would happen by itself in an actual request)
        self.portal.REQUEST.set(FACTORY_INFO, {})


    def testTempObjectLocalRolesBug(self):
        # Evil monkey patch should not change all objects of a class
        self.createMemberarea('member')
        member = self.membership.getMemberById('member')

        # Make an unrelated non-temporary object for comparison
        self.login('manager')
        self.portal.invokeFactory('Document', id='nontmp_id')
        nontemp_object = getattr(self.portal, 'nontmp_id')

        # Assume identify of the ordinary member
        self.login('member')
        folder = self.membership.getHomeFolder()
        temp_object = folder.restrictedTraverse('portal_factory/Document/tmp_id')

        # Make sure member is owner of temporary object
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Member', 'Owner'))
        self.assertEqual(temp_object.Creator(), 'member')

        # Make sure member is not owner of non-temporary object
        # (i.e. make sure our evil monkey patch of the temporary instance has
        # not resulted in our patching all instances of the class)
        self.assertEqual(sortTuple(member.getRolesInContext(nontemp_object)),
                         ('Authenticated', 'Member'))

    def testTempFolderPermissions(self):
        # TempFolder should "inherit" permission mappings from container
        previous_roles = [r for r in self.folder.rolesOfPermission(AddPortalContent) if r['name'] == 'Anonymous']
        self.folder.manage_permission(AddPortalContent, ['Anonymous'], 1)
        new_roles = [r for r in self.folder.rolesOfPermission(AddPortalContent) if r['name'] == 'Anonymous']
        self.failIfEqual(previous_roles, new_roles)

        temp_folder = self.folder.restrictedTraverse(
                                'portal_factory/Document/tmp_id').aq_parent
        temp_roles = [r for r in temp_folder.rolesOfPermission(AddPortalContent) if r['name'] == 'Anonymous']

        self.assertEqual(temp_roles, new_roles)


class TestCreateObject(PloneTestCase.PloneTestCase):

    def testCreateObjectByDoCreate(self):
        # doCreate should create the real object
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        foo = temp_object.portal_factory.doCreate(temp_object, 'foo')
        self.failUnless('foo' in self.folder.objectIds())
        self.assertEqual(foo.get_local_roles_for_userid(default_user), ('Owner',))

    def testUnauthorizedToCreateObjectByDoCreate(self):
        # Anonymous should not be able to create the (real) object
        # Note that Anonymous used to be able to create the temp object...
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.logout()
        self.assertRaises(Unauthorized, temp_object.portal_factory.doCreate,
                          temp_object, 'foo')

    def testCreateObjectByDocumentEdit(self):
        # document_edit should create the real object
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        temp_object.document_edit(id='foo', title='Foo', text_format='plain', text='')
        self.failUnless('foo' in self.folder.objectIds())
        self.assertEqual(self.folder.foo.Title(), 'Foo')
        self.assertEqual(self.folder.foo.get_local_roles_for_userid(default_user), ('Owner',))

    def testUnauthorizedToCreateObjectByDocumentEdit(self):
        # Anonymous should not be able to create the (real) object
        # Note that Anonymous used to be able to create the temp object...
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.logout()
        self.assertRaises(Unauthorized, temp_object.document_edit,
                          id='foo', title='Foo', text_format='plain', text='')


class TestCreateObjectByURL(PloneTestCase.FunctionalTestCase):
    '''Weeee, functional tests'''

    def afterSetUp(self):
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:%s' % (default_user, default_password)
        # We want 401 responses, not redirects to a login page
        plugins = self.portal.acl_users.plugins
        plugins.deactivatePlugin( IChallengePlugin, 'credentials_cookie_auth')

        # Enable portal_factory for Document type
        self.factory = self.portal.portal_factory
        self.factory.manage_setPortalFactoryTypes(listOfTypeIds=['Document'])

    def testCreateObject(self):
        # createObject script should make a temp object
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                self.basic_auth)

        self.assertEqual(response.getStatus(), 302) # Redirect to document_edit_form

        # The redirect URL should contain the factory parts
        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.folder_url+'/portal_factory/Document/'))
        # CMFFormController redirects should not do alias translation
        self.failUnless(location.endswith('/edit'))

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

    def testCreateNonGloballyAllowedObject(self):
        # TempFolder allows to create all portal types
        self.portal.portal_types.Document.manage_changeProperties(global_allow=0)
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                self.basic_auth)

        self.assertEqual(response.getStatus(), 302) # Redirect to document_edit_form

        # The redirect URL should contain the factory parts
        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.folder_url+'/portal_factory/Document/'))
        self.failUnless(location.endswith('/edit'))

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

    def testUnauthorizedToViewEditForm(self):
        # Anonymous should not be able to see document_edit_form
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                ) # No basic out info
        # We got redirected to the factory
        self.assertEqual(response.getStatus(), 302)
        newpath = response.getHeader('location')
        proto, host, path, query, fragment = urlparse.urlsplit(newpath)
        # Let's follow it
        response = self.publish(path)
        # And we are forbidden
        self.assertEqual(response.getStatus(), 401) # Unauthorized

    def testUnauthorizedToViewEditFormOfNonFactoryObject(self):
        # Anonymous should not be able to see newsitem_edit_form
        response = self.publish(self.folder_path +
                                '/createObject?type_name=News%20Item',
                                ) # No basic out info

        self.assertEqual(response.getStatus(), 401) # Unauthorized

    def testCreateObjectByDocumentEdit(self):
        # document_edit should create the real object
        response = self.publish(self.folder_path +
            '/portal_factory/Document/tmp_id/document_edit?id=foo&title=Foo&text_format=plain&text=',
            self.basic_auth)

        self.assertEqual(response.getStatus(), 302) # Redirect to document_view
        viewAction = self.portal.portal_types['Document'].getActionInfo('object/view', self.folder.foo)['url']
        self.failUnless(response.getHeader('Location').startswith(viewAction))

        self.failUnless('foo' in self.folder.objectIds())
        self.assertEqual(self.folder.foo.Title(), 'Foo')
        self.assertEqual(self.folder.foo.get_local_roles_for_userid(default_user), ('Owner',))

    def testUnauthorizedToCreateObjectByDocumentEdit(self):
        # Anonymous should not be able to create the real object
        response = self.publish(self.folder_path +
            '/portal_factory/Document/tmp_id/document_edit?id=foo&title=Foo&text_format=plain&text=',
            ) # No basic auth info

        self.assertEqual(response.getStatus(), 401) # Unauthorized


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalFactory))
    suite.addTest(makeSuite(TestCreateObject))
    suite.addTest(makeSuite(TestCreateObjectByURL))
    return suite
