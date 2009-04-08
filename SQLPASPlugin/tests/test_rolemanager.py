from Testing import ZopeTestCase
from Products.SQLPASPlugin.tests import basetestcase
from AccessControl import getSecurityManager

from logging import ERROR
from logging import NOTSET
from logging import disable

from Products.SQLPASPlugin.config import ROLEMANAGER_ID
from Products.SQLPASPlugin.config import ROLES_COL_USERNAME
from Products.SQLPASPlugin.config import ROLES_COL_ROLENAME
from Products.SQLPASPlugin.tests.config import TESTING_ROLES_TABLE
from Products.PluggableAuthService.utils import createViewName

_marker = []


class TestRoleManager(basetestcase.BaseTestCase):

    def afterSetUp(self):
        self.plugin = self.getPAS()[ROLEMANAGER_ID]

    def queryGetRoles(self, username):
        return 'SELECT %s FROM %s WHERE %s="%s"' % (
                   ROLES_COL_ROLENAME, TESTING_ROLES_TABLE,
                   ROLES_COL_USERNAME, username)

    def queryRemoveRoles(self, username):
        return 'DELETE FROM %s WHERE %s="%s"' % (
                   TESTING_ROLES_TABLE, ROLES_COL_USERNAME, username)

    def queryAddRole(self, username, role):
        return 'INSERT INTO %s (%s, %s) VALUES ("%s", "%s")' % (
                   TESTING_ROLES_TABLE, ROLES_COL_USERNAME,
                   ROLES_COL_ROLENAME, username, role)

    def testDoAssignRoleToPrincipal(self):
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 0)

        self.plugin.doAssignRoleToPrincipal('User1', 'First')
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 1)
        self.assertEqual(tuple(result[0]), ('First',))

        self.plugin.doAssignRoleToPrincipal('User1', 'Second')
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 2)
        self.assertEqual(tuple(result[0]), ('First',))
        self.assertEqual(tuple(result[1]), ('Second',))

        self.plugin.doAssignRoleToPrincipal('User2', 'Third')
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 2)
        self.assertEqual(tuple(result[0]), ('First',))
        self.assertEqual(tuple(result[1]), ('Second',))
        result = self.execute(self.queryGetRoles('User2'))
        self.assertEqual(len(result), 1)
        self.assertEqual(tuple(result[0]), ('Third',))

    def testDoAssignRoleToPrincipalWithMapping(self):
        self.plugin.roles_mapping = [
            '1/First',
            '2/Second',
            'god/Manager',
        ]
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 0)

        self.plugin.doAssignRoleToPrincipal('User1', 'First')
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 1)
        self.assertEqual(tuple(result[0]), ('1',))

        self.plugin.doAssignRoleToPrincipal('User1', 'Second')
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 2)
        self.assertEqual(tuple(result[0]), ('1',))
        self.assertEqual(tuple(result[1]), ('2',))

        self.plugin.doAssignRoleToPrincipal('User2', 'Manager')
        result = self.execute(self.queryGetRoles('User1'))
        self.assertEqual(len(result), 2)
        self.assertEqual(tuple(result[0]), ('1',))
        self.assertEqual(tuple(result[1]), ('2',))
        result = self.execute(self.queryGetRoles('User2'))
        self.assertEqual(len(result), 1)
        self.assertEqual(tuple(result[0]), ('god',))
        self.plugin.roles_mapping = []

    def testGetRolesForPrincipal(self):
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ())

        self.execute(self.queryAddRole('User1', 'First'))
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ('First',))

        self.execute(self.queryAddRole('User1', 'Second'))
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ('First', 'Second'))

        self.execute(self.queryAddRole('User2', 'Third'))
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ('First', 'Second'))
        roles = self.plugin.getRolesForPrincipal('User2')
        self.assertEqual(roles, ('Third',))

    def testGetRolesForPrincipalWithMapping(self):
        self.plugin.roles_mapping = [
            '1/First',
            '2/Second',
            'god/Manager',
        ]
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ())

        self.execute(self.queryAddRole('User1', '1'))
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ('First',))

        self.execute(self.queryAddRole('User1', '2'))
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ('First', 'Second'))

        self.execute(self.queryAddRole('User2', 'god'))
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ('First', 'Second'))
        roles = self.plugin.getRolesForPrincipal('User2')
        self.assertEqual(roles, ('Manager',))
        self.plugin.roles_mapping = []

    def testDoNotFailWithWrongSettingWhenGetRolesForPrincipal(self):
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ())
        self.execute(self.queryAddRole('User1', 'First'))

        # Change the roles table to something that doesn't exists
        self.plugin.manage_changeProperties(roles_table='invalid_table')
        disable(ERROR)
        roles = self.plugin.getRolesForPrincipal('User1')
        disable(NOTSET)
        self.assertEqual(roles, ())

        # Restore the roles table
        self.plugin.manage_changeProperties(roles_table=TESTING_ROLES_TABLE)
        roles = self.plugin.getRolesForPrincipal('User1')
        self.assertEqual(roles, ('First',))


class TestRoleCaching(basetestcase.CacheTestCase):
    def afterSetUp(self):
        basetestcase.CacheTestCase.afterSetUp(self)
        self.plugin = self.getPAS().source_roles
        self.plugin.ZCacheable_setManagerId(basetestcase.CACHE_MANAGER_ID)
        self.execute("INSERT INTO %s VALUES ('%s', 'Manager');" %
                (basetestcase.TESTING_ROLES_TABLE, self.username))

    def testIsCacheEnabled(self):
        self.failUnless(self.plugin.ZCacheable_isCachingEnabled())

    def testCacheStartsEmpty(self):
        view_name = createViewName('getRolesForPrincipal', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                default=_marker)

        self.failUnless(user is _marker)

    def testSingleQuery(self):
        self.plugin.getRolesForPrincipal(self.username)
        view_name = createViewName('getRolesForPrincipal', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                default=_marker)
        self.failUnless(user is not _marker)

    def testTwoQueres(self):
        self.plugin.getRolesForPrincipal(self.username)
        self.plugin.getRolesForPrincipal('xx')

        view_name = createViewName('getRolesForPrincipal', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                default=_marker)
        self.failUnless(user is not _marker)

        view_name = createViewName('getRolesForPrincipal', 'xx')
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                default=_marker)
        self.failUnless(user is not _marker)

    def testAssignRoleZapsCache(self):
        self.plugin.getRolesForPrincipal(self.username)
        self.plugin.doAssignRoleToPrincipal(self.username, 'henchman')
        view_name = createViewName('getRolesForPrincipal', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                default=_marker)
        self.failUnless(user is _marker)

    def testAssignRoleKeepsCacheIfToldSo(self):
        self.plugin.getRolesForPrincipal(self.username)
        self.plugin.doAssignRoleToPrincipal(self.username, 'henchman', True)
        view_name = createViewName('getRolesForPrincipal', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                default=_marker)
        self.failUnless(user is not _marker)

    def testAssignRolesZapsCache(self):
        self.plugin.getRolesForPrincipal(self.username)
        self.plugin.assignRolesToPrincipal(self.username, ('henchman',))
        view_name = createViewName('getRolesForPrincipal', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                default=_marker)
        self.failUnless(user is _marker)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRoleManager))
    suite.addTest(makeSuite(TestRoleCaching))
    return suite
