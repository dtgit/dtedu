from Testing import ZopeTestCase
from Products.SQLPASPlugin.tests import basetestcase
from Products.SQLPASPlugin import config
from Products.SQLPASPlugin.plugins import usermanager
from Products.PluggableAuthService.utils import createViewName

_marker = []

class TestUserManager(basetestcase.BaseTestCase):

    def afterSetUp(self):
        self.username = 'joe'
        self.password = 'password'
        self.plugin = self.getPAS()[config.USERMANAGER_ID]

    def testDoAddUser(self):
        self.plugin.doAddUser(self.username, self.password)
        ret = self.plugin.enumerateUsers(id=self.username, exact_match=True)
        self.assertEqual(len(ret), 1)

    def testRemoveUser(self):
        ret = self.plugin.enumerateUsers(id=self.username, exact_match=True)
        self.assertEqual(len(ret), 0)
        self.plugin.doAddUser(self.username, self.password)
        self.plugin.removeUser(self.username)
        ret = self.plugin.enumerateUsers(id=self.username, exact_match=True)
        self.assertEqual(len(ret), 0)

    def testAuthenticateCredentials(self):
        auth = self.plugin.authenticateCredentials({'login': self.username,
                                                          'password': self.password})
        self.assertEqual(auth, None)

        self.plugin.doAddUser(self.username, self.password)
        auth = self.plugin.authenticateCredentials({'login': self.username,
                                                          'password': self.password})
        self.assertEqual(auth, (self.username, self.username))

    def testStructure(self):
        self.assertEqual(len(self.plugin.objectIds()),
                         len(usermanager._SQL_QUERIES))


class TestEnumerateUsers(basetestcase.BaseTestCase):

    def afterSetUp(self):
        self.plugin = self.getPAS()[config.USERMANAGER_ID]
        self.plugin.doAddUser('user_1', 'password')
        self.plugin.doAddUser('user_2', 'password')
        self.plugin.doAddUser('foo_user_1', 'password')
        self.plugin.doAddUser('bar', 'password')

    def testNoIdAndNoLoginNoExact(self):
        ret = self.plugin.enumerateUsers()
        self.assertEqual(len(ret), 4)

    def testNoIdAndNoLoginExact(self):
        ret = self.plugin.enumerateUsers(exact_match=True)
        self.assertEqual(len(ret), 0)

    def testReturnFormat(self):
        ret = self.plugin.enumerateUsers(id='user_1', exact_match=True)
        expected = (dict(login='user_1', pluginid='source_users', id= 'user_1'),)
        self.assertEqual(ret, expected)

    def testIdStringNoExact(self):
        ret = self.plugin.enumerateUsers(id='user_1')
        self.assertEqual(len(ret), 2) # user_1, foo_user_1

    def testIdEqualLogin(self):
        ret = self.plugin.enumerateUsers(id='user_1', login='user_1')
        self.assertEqual(len(ret), 2) # user_1, foo_user_1

    def testLoginStringExact(self):
        ret = self.plugin.enumerateUsers(login='user', exact_match=True)
        self.assertEqual(ret, ())

    def testLoginStringNoExact(self):
        ret = self.plugin.enumerateUsers(login='user')
        self.assertEqual(len(ret), 3) # all but bar

    def testLoginListExact(self):
        ret = self.plugin.enumerateUsers(login=['user_1', '2'], exact_match=True)
        self.assertEqual(len(ret), 1) # user_1

    def testLoginListNoExact(self):
        ret = self.plugin.enumerateUsers(login=['user_0', '2'])
        self.assertEqual(len(ret), 1) # user_2

    def testIdListExact(self):
        ret = self.plugin.enumerateUsers(id=['user_1', 'foo'], exact_match=True)
        self.assertEqual(len(ret), 1) # user_1

    def testIdListNoExact(self):
        ret = self.plugin.enumerateUsers(id=['user_1', 'foo'])
        self.assertEqual(len(ret), 2) # user_1, foo_user_11

    def testIdStringAndLoginStringNoExact(self):
        ret = self.plugin.enumerateUsers(id='user_1', login='bar')
        self.assertEqual(len(ret), 3) # user_1, foo_user_11, bar

    def testIdStringAndLoginStringExact(self):
        ret = self.plugin.enumerateUsers(id='user', login='bar', exact_match=True)
        self.assertEqual(len(ret), 1) # bar

    def testIdListAndLoginStringNoExact(self):
        ret = self.plugin.enumerateUsers(id=['2', '3'], login='4')
        self.assertEqual(len(ret), 1) # user_2

    def testIdStringAndLoginListNoExact(self):
        ret = self.plugin.enumerateUsers(id='5', login=['0', '2', '8'])
        self.assertEqual(len(ret), 1) # user_2

    def testMaxResultsZero(self):
        ret = self.plugin.enumerateUsers(max_results=0)
        self.assertEqual(len(ret), 0)

    def testMaxResultsFixed(self):
        ret = self.plugin.enumerateUsers(max_results=3)
        self.assertEqual(len(ret), 3)

    def testMaxResultsAbove(self):
        ret = self.plugin.enumerateUsers(max_results=10)
        self.assertEqual(len(ret), 4)


class TestGetUserInfoCaching(basetestcase.CacheTestCase):
    def testIsCacheEnabled(self):
        self.failUnless(self.plugin.ZCacheable_isCachingEnabled())

    def testInitialUserCacheIsEmpty(self):
        view_name = createViewName('getUserInfo', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=dict(auth=False),
                default=_marker)
        self.failUnless(user is _marker)

    def testNoAuthGetUserIsCached(self):
        self.plugin.getUserInfo(self.username, auth=False)
        view_name = createViewName('getUserInfo', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=dict(auth=False),
                default=_marker)
        self.failUnless(user is not _marker)

    def testAuthGetUserIsNotCached(self):
        config.CACHE_PASSWORDS=False
        self.plugin.getUserInfo(self.username, auth=True)
        view_name = createViewName('getUserInfo', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=dict(auth=True),
                default=_marker)
        self.failUnless(user is _marker)

    def testAuthGetUserIsCachedIfWeSaySo(self):
        config.CACHE_PASSWORDS=True
        self.plugin.getUserInfo(self.username, auth=True)
        config.CACHE_PASSWORDS=False
        view_name = createViewName('getUserInfo', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=dict(auth=True),
                default=_marker)
        self.failUnless(user is not _marker)

    def testRemoveUserInvalidatesCache(self):
        config.CACHE_PASSWORDS=True

        # Prime our caches
        self.plugin.getUserInfo(self.username, auth=False)
        self.plugin.getUserInfo(self.username, auth=True)

        # Remove a user should invalidate all her cache entries
        self.plugin.removeUser(self.username)

        view_name = createViewName('getUserInfo', self.username)
        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=dict(auth=False),
                default=_marker)
        self.failUnless(user is _marker)

        user = self.plugin.ZCacheable_get(
                view_name=view_name,
                keywords=dict(auth=True),
                default=_marker)
        self.failUnless(user is _marker)


class TestUserManagerCache(basetestcase.CacheTestCase):

    def testEnumerateUsersIsCaching(self):
        view_name = createViewName('enumerateUsers', None)
        keywords = dict(id=None, login=None, exact_match=False,
                sort_by=None, max_results=None)

        # Cache is initially empty
        cache=self.plugin.ZCacheable_get(view_name=view_name, keywords=keywords)
        self.failUnless(cache is None)

        # After the first enumerateUsers call, we should have cached data
        results = self.plugin.enumerateUsers()
        cache = self.plugin.ZCacheable_get(view_name=view_name,
                keywords=keywords)
        expected = (dict(login=self.username,
                                pluginid='source_users',
                                id=self.username),)
        self.assertEqual(cache, expected)


    def testEnumerateUsersIsCachingPerUser(self):
        view_name1 = createViewName('enumerateUsers', self.username)
        view_name2 = createViewName('enumerateUsers', 'foo')
        keywords1 = dict(id=None, login=[self.username], exact_match=False,
                sort_by=None, max_results=None)
        keywords2 = dict(id=None, login=['foo'], exact_match=False,
                sort_by=None, max_results=None)

        # Caches are initially empty
        cache1 = self.plugin.ZCacheable_get(view_name=view_name1,
                keywords=keywords1)
        self.assertEqual(cache1, None)
        cache2 = self.plugin.ZCacheable_get(view_name=view_name2,
                keywords=keywords2)
        self.assertEqual(cache2, None)

        # After the first enumerateUsers call we should have cached data
        results1 = self.plugin.enumerateUsers(login=self.username)
        cache1 = self.plugin.ZCacheable_get(view_name=view_name1,
                keywords=keywords1)
        expected1 = (dict(login=self.username,
                          pluginid='source_users',
                          id=self.username),)
        self.assertEqual(cache1, expected1)

        cache2 = self.plugin.ZCacheable_get(view_name=view_name2,
                keywords=keywords2)
        self.assertEqual(cache2, None)

        # When doing a different query, the previous cache should still exist
        results2 = self.plugin.enumerateUsers(login='foo')
        cache1 = self.plugin.ZCacheable_get(view_name=view_name1,
                keywords=keywords1)
        self.assertEqual(cache1, expected1)

        cache2 = self.plugin.ZCacheable_get(view_name=view_name2,
                keywords=keywords2)
        expected2 = tuple()
        self.assertEqual(cache2, expected2)


    def testAddUserInvalidatesUserEnumerateCaches(self):
        view_name1 = createViewName('enumerateUsers')
        view_name2 = createViewName('enumerateUsers', self.username)
        keywords1 = dict(id=None, login=None, exact_match=False,
                sort_by=None, max_results=None)
        keywords2 = dict(id=None, login=[self.username], exact_match=False,
                sort_by=None, max_results=None)

        # Prime the caches
        self.plugin.enumerateUsers()
        self.plugin.enumerateUsers(login=self.username)

        # Adding a user should clear our cache again
        self.plugin.doAddUser('foo', self.password)

        cache1 = self.plugin.ZCacheable_get(view_name=view_name1,
                keywords=keywords1)
        self.assertEqual(cache1, None)
        cache2 = self.plugin.ZCacheable_get(view_name=view_name2,
                keywords=keywords2)
        self.assertEqual(cache2, None)

    def testRemoveUserInvalidatesEnumerateCaches(self):
        view_name1 = createViewName('enumerateUsers')
        view_name2 = createViewName('enumerateUsers', self.username)
        keywords1 = dict(id=None, login=None, exact_match=False,
                sort_by=None, max_results=None)
        keywords2 = dict(id=None, login=[self.username], exact_match=False,
                sort_by=None, max_results=None)

        # Prima the caches
        self.plugin.enumerateUsers()
        self.plugin.enumerateUsers(login=self.username)

        # Removing a user should clear the caches
        self.plugin.removeUser(self.username)
        
        cache1 = self.plugin.ZCacheable_get(view_name=view_name1,
                keywords=keywords1)
        self.assertEqual(cache1, None)
        cache2 = self.plugin.ZCacheable_get(view_name=view_name2,
                keywords=keywords2)
        self.assertEqual(cache2, None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserManager))
    suite.addTest(makeSuite(TestEnumerateUsers))
    suite.addTest(makeSuite(TestGetUserInfoCaching))
    suite.addTest(makeSuite(TestUserManagerCache))
    return suite
