import copy
import plugin_exceptions

from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from ZODB.POSException import ConflictError
from App.class_init import default__class_init__ as InitializeClass

from Products.PluggableAuthService.utils import createViewName
from Products.PluggableAuthService.utils import classImplements

from Products.PluggableAuthService.interfaces.plugins \
    import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins \
    import IUserEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins \
    import IUserAdderPlugin

from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.permissions import SetOwnPassword

from Products.SQLPASPlugin.utils import logEx
from Products.SQLPASPlugin import encrypt

from Products.PlonePAS.interfaces.plugins import IUserManagement
from Products.PlonePAS.interfaces.capabilities import IDeleteCapability
from Products.PlonePAS.interfaces.capabilities import IPasswordSetCapability

from Products.SQLPASPlugin.plugins.sql import SQLBase
from Products.SQLPASPlugin import config

manage_addSQLUserManagerForm = DTMLFile("../zmi/UserManagerForm", globals())

_marker = []

def manage_addSQLUserManager(self, id, title='', sql_connection='', REQUEST=None):
    """Add a SQLUserManager to a Pluggable Auth Service."""
    um = SQLUserManager(id, title, sql_connection)
    self._setObject(um.getId(), um)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'SQLUserManager+added.'
                            % self.absolute_url())

class SQLUserManager(SQLBase):
    """PAS plugin for managing users in a SQL-based database.

    Based on PluggableAuthService/plugins/ZODBUserManager.py
    implementation.
    """
    meta_type = 'SQL User Manager'
    security = ClassSecurityInfo()

    _properties = SQLBase._properties + (
        {'id':'default_encryption', 'type': 'string', 'mode': 'w'},
     )

    default_encryption = encrypt.DEFAULT_ENCRYPTION

    security.declarePrivate('invalidateCacheForChangedUser')
    def invalidateCacheForChangedUser(self, user_id):
        view_name = createViewName('enumerateUsers')
        self.ZCacheable_invalidate(view_name=view_name)
        view_name = createViewName('enumerateUsers', user_id)
        self.ZCacheable_invalidate(view_name=view_name)
        view_name = createViewName('getUserInfo', user_id)
        self.ZCacheable_invalidate(view_name=view_name)

    #
    # SQLBase
    #
    security.declarePrivate('getSchemaConfig')
    def getSchemaConfig(self):
        return dict(users_table=self.getProperty('users_table'),
                    username_col=self.getProperty('users_col_username'),
                    password_col=self.getProperty('users_col_password'))

    security.declarePrivate('getSQLQueries')
    def getSQLQueries(self):
        return _SQL_QUERIES

    #
    # IUserManagement implementation
    #
    security.declarePrivate('doChangeUser')
    def doChangeUser(self, login, password, **kw):
        self.updateUserPassword(login, login, password)

    security.declarePrivate('doDeleteUser')
    def doDeleteUser(self, login):
        try:
            self.removeUser(login)
        except KeyError:
            return False
        return True

    #
    # IDeleteCapability implementation
    #
    def allowDeletePrincipal(self, id):
        """True if this plugin can delete a certain user/group."""
        info = self.getUserInfo(id)
        return info is not None

    #
    # IPasswordSetCapability implementation
    #
    def allowPasswordSet(self, id):
        """True if this plugin can set the password of a certain user."""
        info = self.getUserInfo(id)
        return info is not None

    #
    # IAuthenticationPlugin implementation
    #
    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """See IAuthenticationPlugin.

        o We expect the credentials to be those returned by
          ILoginPasswordExtractionPlugin.
        """
        login = credentials.get('login')
        password = credentials.get('password')

        if login is None or password is None:
            return None

        user = self.getUserInfo(login, auth=True)
        if user:
            encrypter = encrypt.find_encrypter(self.default_encryption)
            if encrypter is None:
                raise LookupError('Could not find an encrypter for "%s"'
                                  % self.default_encryption)

            if encrypter.validate(user['password'], password):
                return login, login

        return None

    #
    # IUserEnumerationPlugin implementation
    #
    security.declarePrivate('enumerateUsers')
    def enumerateUsers( self
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):
        """See IUserEnumerationPlugin.
        """
        view_name = createViewName('enumerateUsers', id or login)

        if isinstance(id, str):
            id = [id]
        if isinstance(login, str):
            login = [login]

        # Check cached data
        keywords = copy.deepcopy(kw)
        info = {
            'id': id,
            'login': login,
            'exact_match': exact_match,
            'sort_by': sort_by,
            'max_results': max_results,
        }
        keywords.update(info)
        cached_info = self.ZCacheable_get(view_name=view_name,
                                          keywords=keywords)
        if cached_info is not None:
            return cached_info

        terms = []
        if id is not None:
            terms.extend(id)
        if login is not None:
            terms.extend(login)

        results = []
        if exact_match:
            for term in terms:
                for info in self.sqlLoadUser(username=term).tuples():
                    results.append(info)
        else:
            # XXX this should really do a glob-match on the SQL side of things
            results = self.sqlLoadAllUsers().tuples()

        all = {}
        for n, record in enumerate(results):
            user_id = record[0]
            data = {
                'id': user_id,
                'login': user_id,
                'pluginid': self.getId(),
            }

            if max_results is not None and len(all) == max_results:
                break

            if exact_match or not terms:
                all.setdefault(user_id, data)
            else:
                for term in terms:
                    if term in user_id:
                        all.setdefault(user_id, data)
                        if max_results is not None and len(all) == max_results:
                            break

        values = tuple(all.values())

        # Cache data upon success
        self.ZCacheable_set(values, view_name=view_name, keywords=keywords)

        return values

    #
    # IUserAdderPlugin implementation
    #
    security.declarePrivate('doAddUser')
    def doAddUser(self, login, password):
        try:
            self.addUser(login, login, password)
        except KeyError:
            return False
        return True

    #
    # (notional)IZODBUserManager interface
    #
    security.declareProtected(ManageUsers, 'listUserIds')
    def listUserIds(self):
        res = self.sqlLoadAllUsers()
        tuples = res.tuples()
        all = [row['username'] for row in tuples]
        return tuple(all)


    security.declareProtected(ManageUsers, 'getUserInfo')
    def getUserInfo(self, user_id, auth=False):
        view_name = createViewName('getUserInfo', user_id)
        keywords = dict(auth=auth)
        
        if config.CACHE_PASSWORDS or not auth:
            cached_info = self.ZCacheable_get(view_name=view_name,
                    keywords=keywords,
                    default=_marker)
            if cached_info is not _marker:
                return cached_info

        try:
            if auth:
                res = self.sqlAuthUser(username=user_id)
            else:
                res = self.sqlLoadUser(username=user_id)
        except ConflictError:
            raise
        except:
            logEx("Error while trying to query user")

        tuples = res.tuples()
        if len(tuples) > 1:
            raise plugin_exceptions.UnexpectedResultsException \
                ("The username column is not unique, found multiple " \
                 "records for user '%s'" % user_id)


        if tuples:
            record = tuples[0]
            data = {
                'id': record[0],
                'login': record[0],
                'pluginid': self.getId(),
            }
            if auth:
                data['password'] = record[1]
        else:
            data = None

        if config.CACHE_PASSWORDS or not auth:
            self.ZCacheable_set(data, view_name=view_name, keywords=keywords)

        return data

    security.declareProtected(ManageUsers, 'listUserInfo')
    def listUserInfo(self):
        res = self.sqlLoadAllUsers()
        tuples = res.tuples()
        return tuples

    security.declareProtected(ManageUsers, 'getUserIdForLogin')
    def getUserIdForLogin(self, login_name):
        return login_name

    security.declareProtected(ManageUsers, 'getLoginForUserId')
    def getLoginForUserId(self, user_id):
        return user_id

    security.declarePrivate('addUser')
    def addUser(self, user_id, login_name, password):
        encrypter = encrypt.find_encrypter(self.default_encryption)
        if encrypter is None:
            raise LookupError('Could not find an encrypter for "%s"'
                              % self.default_encryption)
        password = encrypter.encrypt(password)

        existingUser = self.getUserInfo(user_id)
        if existingUser:
            raise KeyError, 'Duplicate user ID: %s' % user_id
        self.sqlCreateUser(username=login_name, password=password)
        self.invalidateCacheForChangedUser(user_id)

    security.declarePrivate('updateUser')
    def updateUser(self, user_id, login_name):
        pass

    security.declarePrivate('removeUser')
    def removeUser(self, user_id):
        existingUser = self.getUserInfo(user_id)
        if existingUser is None:
            raise KeyError, 'Invalid user ID: %s' % user_id
        self.sqlRemoveUser(username=user_id)
        self.invalidateCacheForChangedUser(user_id)

    security.declarePrivate('updateUserPassword')
    def updateUserPassword(self, user_id, login_name, password):
        existingUser = self.getUserInfo(user_id)
        if existingUser is None:
            raise KeyError, 'Invalid user ID: %s' % user_id

        encrypter = encrypt.find_encrypter(self.default_encryption)
        if encrypter is None:
            raise LookupError('Could not find an encrypter for "%s"'
                              % self.default_encryption)
        self.sqlUpdateUser(username=login_name,
                           password=encrypter.encrypt(password))

    #
    # Allow users to change their own login name and password.
    #
    security.declareProtected(SetOwnPassword, 'getOwnUserInfo')
    def getOwnUserInfo(self):
        """Return current user's info."""
        user_id = getSecurityManager().getUser().getId()
        return self.getUserInfo(user_id)


classImplements(SQLUserManager,
                IAuthenticationPlugin,
                IUserEnumerationPlugin,
                IUserAdderPlugin,
                IUserManagement,
                IDeleteCapability,
                IPasswordSetCapability)

InitializeClass(SQLUserManager)

_SQL_QUERIES = (

    (
     "sqlAuthUser",
     "Retrieve a user and password",
     "username",
     """
SELECT %(username_col)s as username, %(password_col)s as password
FROM %(users_table)s
WHERE %(username_col)s=<dtml-sqlvar username type=string>
     """
    ),

    (
     "sqlLoadUser",
     "Retrieve a user",
     "username",
     """
SELECT %(username_col)s as username
FROM %(users_table)s
WHERE %(username_col)s=<dtml-sqlvar username type=string>
     """
    ),

    (
     "sqlLoadAllUsers",
     "Retrieve all users",
     "",
     """
SELECT %(username_col)s as username
FROM %(users_table)s
     """
    ),

    (
     "sqlCreateUser",
     "Create a new user",
     "username password",
     """
INSERT INTO %(users_table)s (%(username_col)s, %(password_col)s)
VALUES (<dtml-sqlvar username type=string>,
        <dtml-sqlvar password type=string>)
     """
    ),

    (
     "sqlRemoveUser",
     "Remove a user",
     "username password",
     """
DELETE FROM %(users_table)s
WHERE %(username_col)s=<dtml-sqlvar username type=string>
     """
    ),

    (
     "sqlUpdateUser",
     "Update user info",
     "username password",
     """
UPDATE %(users_table)s
SET %(password_col)s=<dtml-sqlvar password type=string>
WHERE %(username_col)s=<dtml-sqlvar username type=string>
     """
    ),

)
