import unittest
import Testing

from Products.CMFCore.tests.base.testcase import SecurityTest


class CoreUtilsTests(unittest.TestCase):

    def test_normalize(self):
        from Products.CMFCore.utils import normalize

        self.assertEqual( normalize('foo/bar'), 'foo/bar' )
        self.assertEqual( normalize('foo\\bar'), 'foo/bar' )

    def test_keywordsplitter_empty(self):
        from Products.CMFCore.utils import keywordsplitter

        for x in [ '', ' ', ',', ',,', ';', ';;' ]:
            self.assertEqual( keywordsplitter({'Keywords': x}), 
                              [] )

    def test_keywordsplitter_single(self):
        from Products.CMFCore.utils import keywordsplitter

        for x in [ 'foo', ' foo ', 'foo,', 'foo ,,', 'foo;', 'foo ;;' ]:
            self.assertEqual( keywordsplitter({'Keywords': x}), 
                              ['foo'] )

    def test_keywordsplitter_multi(self):
        from Products.CMFCore.utils import keywordsplitter

        for x in [ 'foo, bar, baz'
                 , 'foo, bar , baz'
                 , 'foo, bar,, baz'
                 , 'foo; bar; baz'
                 ]:
            self.assertEqual( keywordsplitter({'Keywords': x}), 
                              ['foo', 'bar', 'baz'] )

    def test_contributorsplitter_emtpy(self):
        from Products.CMFCore.utils import contributorsplitter

        for x in [ '', ' ', ';', ';;' ]:
            self.assertEqual( contributorsplitter({'Contributors': x}), 
                              [] )

    def test_contributorsplitter_single(self):
        from Products.CMFCore.utils import contributorsplitter

        for x in [ 'foo', ' foo ', 'foo;', 'foo ;;' ]:
            self.assertEqual( contributorsplitter({'Contributors': x}), 
                              ['foo'] )

    def test_contributorsplitter_multi(self):
        from Products.CMFCore.utils import contributorsplitter

        for x in [ 'foo; bar; baz'
                 , 'foo; bar ; baz'
                 , 'foo; bar;; baz'
                 ]:
            self.assertEqual( contributorsplitter({'Contributors': x}), 
                              ['foo', 'bar', 'baz'] )

    def test_getPackageName(self):
        from Products.CMFCore.utils import getPackageName
        from Products.CMFCore.utils import _globals

        self.assertEqual(getPackageName(globals()), 'Products.CMFCore.tests')
        self.assertEqual(getPackageName(_globals), 'Products.CMFCore')

    def test_getContainingPackage(self):
        from Products.CMFCore.utils import getContainingPackage

        self.assertEqual(getContainingPackage('Products.CMFCore.exceptions'),
                'Products.CMFCore')
        self.assertEqual(getContainingPackage('Products.CMFCore'),
                'Products.CMFCore')
        self.assertEqual(getContainingPackage('zope.interface.verify'),
                'zope.interface')


class CoreUtilsSecurityTests(SecurityTest):

    def _makeSite(self):
        from AccessControl.Owned import Owned
        from Products.CMFCore.tests.base.dummy import DummySite
        from Products.CMFCore.tests.base.dummy import DummyUserFolder
        from Products.CMFCore.tests.base.dummy import DummyObject

        class _DummyObject(Owned, DummyObject):
            pass

        site = DummySite('site').__of__(self.root)
        site._setObject( 'acl_users', DummyUserFolder() )
        site._setObject('foo_dummy', _DummyObject(id='foo_dummy'))
        site._setObject('bar_dummy', _DummyObject(id='bar_dummy'))

        return site

    def test__checkPermission(self):
        from AccessControl import getSecurityManager
        from AccessControl.ImplPython import ZopeSecurityPolicy
        from AccessControl.Permission import Permission
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy
        from Products.CMFCore.utils import _checkPermission

        setSecurityPolicy(ZopeSecurityPolicy())
        site = self._makeSite()
        newSecurityManager(None, site.acl_users.user_foo)
        o = site.bar_dummy
        Permission('View',(),o).setRoles(('Anonymous',))
        Permission('WebDAV access',(),o).setRoles(('Authenticated',))
        Permission('Manage users',(),o).setRoles(('Manager',))
        eo = site.foo_dummy
        eo._owner = (['acl_users'], 'all_powerful_Oz')
        getSecurityManager().addContext(eo)
        self.failUnless( _checkPermission('View', o) )
        self.failUnless( _checkPermission('WebDAV access', o) )
        self.failIf( _checkPermission('Manage users', o) )

        eo._proxy_roles = ('Authenticated',)
        self.failIf( _checkPermission('View', o) )
        self.failUnless( _checkPermission('WebDAV access', o) )
        self.failIf( _checkPermission('Manage users', o) )

        eo._proxy_roles = ('Manager',)
        self.failIf( _checkPermission('View', o) )
        self.failIf( _checkPermission('WebDAV access', o) )
        self.failUnless( _checkPermission('Manage users', o) )

    def test_mergedLocalRolesManipulation(self):
        # The _mergedLocalRoles function used to return references to
        # actual local role settings and it was possible to manipulate them
        # by changing the return value. http://www.zope.org/Collectors/CMF/376
        from Products.CMFCore.tests.base.dummy import DummyContent
        from Products.CMFCore.utils import _mergedLocalRoles
        obj = DummyContent()
        obj.manage_addLocalRoles('dummyuser1', ['Manager', 'Owner'])
        self.assertEqual(len(obj.get_local_roles_for_userid('dummyuser1')), 2)

        merged_roles = _mergedLocalRoles(obj)
        merged_roles['dummyuser1'].append('FOO')

        # The values on the object itself should still the the same
        self.assertEqual(len(obj.get_local_roles_for_userid('dummyuser1')), 2)


def test_suite():
    # reimport to make sure tests are run from Products
    from Products.CMFCore.tests.test_utils import CoreUtilsTests

    return unittest.TestSuite((
        unittest.makeSuite(CoreUtilsTests),
        unittest.makeSuite(CoreUtilsSecurityTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
