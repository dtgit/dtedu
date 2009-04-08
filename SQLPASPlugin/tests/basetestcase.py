__author__  = '''Rocky Burt <rocky@serverzen.com>'''
__docformat__ = 'plaintext'

import os
from Testing import ZopeTestCase
from zope.component import testing

import transaction
import Products.Five
import Products.SQLPASPlugin
from Products.Five import zcml

from Products.SQLPASPlugin import utils
from Products.SQLPASPlugin import encrypt

from Products.SQLPASPlugin.config import USERMANAGER_ID
from Products.SQLPASPlugin.config import ROLEMANAGER_ID
from Products.SQLPASPlugin.config import PROPERTYPROVIDER_ID
from Products.SQLPASPlugin.tests.config import TESTING_DB
from Products.SQLPASPlugin.tests.config import TESTING_DB_EXTRA
from Products.SQLPASPlugin.tests.config import TESTING_USERS_TABLE
from Products.SQLPASPlugin.tests.config import TESTING_ROLES_TABLE
from Products.SQLPASPlugin.tests.config import TESTING_USERS_COLUMNS
from Products.SQLPASPlugin.tests.config import TESTING_ROLES_COLUMNS

from Products.PlonePAS.Extensions import Install as ppasinstall

ZopeTestCase.installProduct('PlonePAS')
ZopeTestCase.installProduct('SQLPASPlugin')
ZopeTestCase.installProduct('PluggableAuthService')
ZopeTestCase.installProduct('StandardCacheManagers')

if TESTING_DB == 'postgresql':
    ZopeTestCase.installProduct('ZPsycopgDA')
elif TESTING_DB == 'mysql':
    ZopeTestCase.installProduct('ZMySQLDA')
elif TESTING_DB == 'sqlite':
    ZopeTestCase.installProduct('ZSQLiteDA')
else:
    raise RuntimeError("%r is not a valid value for the TESTING_DB, "
                       "Please correct." % TESTING_DB)

SANDBOX_ID = 'sandbox'
CONNECTION_ID = 'db_con'
CACHE_MANAGER_ID = 'cm_test'

class SQLLayer:

    @classmethod
    def setUp(cls):
        testing.setUp()
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('encrypt.zcml', Products.SQLPASPlugin)

        app = ZopeTestCase.app()

        # Create our sandbox
        app.manage_addFolder(SANDBOX_ID)
        sandbox = app[SANDBOX_ID]

        # Add a cache manager
        factory = sandbox.manage_addProduct['StandardCacheManagers']
        factory.manage_addRAMCacheManager(CACHE_MANAGER_ID)

        # Setup the DB connection and PAS instances
        cls.conn = cls.setupConnection(sandbox)
        cls.pas = cls.setupPAS(sandbox)

        # Update PAS to use test tables
        users = cls.pas[USERMANAGER_ID]
        users.manage_changeProperties(users_table=TESTING_USERS_TABLE)
        roles = cls.pas[ROLEMANAGER_ID]
        roles.manage_changeProperties(roles_table=TESTING_ROLES_TABLE)
        props = cls.pas[PROPERTYPROVIDER_ID]
        props.manage_changeProperties(users_table=TESTING_USERS_TABLE)

        # Create the tables tests
        cls.execute(cls.createTable(TESTING_USERS_TABLE,
                                    TESTING_USERS_COLUMNS))
        cls.execute(cls.createTable(TESTING_ROLES_TABLE,
                                    TESTING_ROLES_COLUMNS))

        transaction.commit()
        ZopeTestCase.close(app)

    @classmethod
    def tearDown(cls):
        testing.tearDown()
        app = ZopeTestCase.app()

        # Remove the tables tests
        cls.execute('DROP TABLE %s' % TESTING_USERS_TABLE)
        cls.execute('DROP TABLE %s' % TESTING_ROLES_TABLE)

        # Remove our sandbox
        app.manage_delObjects(SANDBOX_ID)

        # Remove the testing sqlite database, if existing
        dbFile = 'sqlpasplugin-testing.db'
        dbDir = os.path.join(os.getenv('INSTANCE_HOME'), 'var', 'sqlite')
        dbPath = os.path.join(dbDir, dbFile)
        if os.path.exists(dbDir):
            os.remove(dbPath)

        transaction.commit()
        ZopeTestCase.close(app)

    @classmethod
    def execute(cls, sql):
        return cls.conn.manage_test(sql)

    @classmethod
    def createTable(cls, table, columns):
        sql = 'CREATE TABLE %s (' % table
        for name, kind, length, extra in columns:
            if length is not None:
                sql += "%s %s(%i) %s, " % (name, kind, length, extra)
            else:
                sql += "%s %s %s, " % (name, kind, extra)
        sql = sql[:-2] + ')'
        return sql

    @classmethod
    def setupConnection(cls, container):
        if TESTING_DB == 'postgresql':
            import Products.ZPsycopgDA
            zpsycopgda = container.manage_addProduct['ZPsycopgDA']
            addConnection = zpsycopgda.manage_addZPsycopgConnection
            addConnection(id=CONNECTION_ID,
                          title='Database Connection',
                          connection_string=TESTING_DB_EXTRA,
                          check=1)

        elif TESTING_DB == 'mysql':
            import Products.ZMySQLDA
            mysqlda = container.manage_addProduct['ZMySQLDA']
            addConnection = mysqlda.manage_addZMySQLConnection
            addConnection(id=CONNECTION_ID,
                          title='Database Connection',
                          connection_string=TESTING_DB_EXTRA,
                          check=1)

        elif TESTING_DB == 'sqlite':
            import Products.ZSQLiteDA
            dbFile = 'sqlpasplugin-testing.db'
            dbDir = os.path.join(os.getenv('INSTANCE_HOME'), 'var', 'sqlite')
            dbPath = os.path.join(dbDir, dbFile)
            if not os.path.exists(dbDir):
                os.makedirs(dbDir)
            elif os.path.exists(dbPath):
                os.remove(dbPath)
            sqliteda = container.manage_addProduct['ZSQLiteDA']
            addSQLite = sqliteda.manage_addZSQLiteConnection
            addSQLite(id=CONNECTION_ID,
                      title='Database Connection',
                      connection=dbFile)
        return getattr(container, CONNECTION_ID)

    @classmethod
    def setupPAS(cls, container):
        factory = container.manage_addProduct['PluggableAuthService']
        factory.addPluggableAuthService(REQUEST=None)
        pas = container.acl_users
        ppasinstall.registerPluginTypes(pas)
        utils.updatePAS(container, CONNECTION_ID)
        return pas


class BaseTestCase(ZopeTestCase.ZopeTestCase):

    layer = SQLLayer

    def afterSetUp(self):
        self.username = 'joe'
        self.password = 'password'

    def execute(self, sql):
        return self.layer.execute(sql)

    def getPAS(self):
        return self.layer.pas

    def beforeTearDown(self):
        self.execute('DELETE FROM %s' % TESTING_USERS_TABLE)
        self.execute('DELETE FROM %s' % TESTING_ROLES_TABLE)


class CacheTestCase(BaseTestCase):
    def afterSetUp(self):
        BaseTestCase.afterSetUp(self)
        self.plugin = self.getPAS()[USERMANAGER_ID]
        self.plugin.ZCacheable_setManagerId(CACHE_MANAGER_ID)
        self.plugin.doAddUser(self.username, self.password)

    def beforeTearDown(self):
        BaseTestCase.beforeTearDown(self)
        self.plugin.ZCacheable_setManagerId(None)


