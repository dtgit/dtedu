from OFS.Cache import Cacheable
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError

from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager

from Products.ZSQLMethods.SQL import SQL
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

from Products.SQLPASPlugin.utils import logEx
from Products.SQLPASPlugin import config as sqlpasconfig

manage_options = list(BasePlugin.manage_options + Cacheable.manage_options)
for opt in Folder.manage_options:
    if opt not in manage_options:
        manage_options.append(opt)
manage_options = tuple(manage_options)


class SafeSQLQuery(Folder):

    all_meta_types = (
        {'name': 'Z SQL Method',
         'action': 'manage_addProduct/ZSQLMethods/add' },
    )

    class Void:
        def tuples(self):
            return ()
        def dictionaries(self):
            return ()

    def __init__(self, id, query):
        Folder.__init__(self, id)
        self._setObject('query', query)

    def __call__(self, *args, **kwargs):
        try:
            return self.query(*args, **kwargs)
        except ConflictError:
            raise
        except:
            logEx("Something went wrong while trying to run the query:\n%r.\n"
                  "Double check the %r plugin properties." %
                  (self.absolute_url(), self.aq_parent.getId()))
            return self.Void()


class SQLBase(Folder, BasePlugin, Cacheable):
    """A base SQL class to be subclassed by the plugins.

    It updates the SafeSQLQuery objects when changing the properties.
    """
    security = ClassSecurityInfo()
    manage_options = manage_options
    mapping = ''

    _properties = (
        {'id':'users_table', 'type': 'string', 'mode': 'w'},
        {'id':'users_col_username', 'type': 'string', 'mode': 'w'},
        {'id':'users_col_password', 'type': 'string', 'mode': 'w'},
    )

    users_table = sqlpasconfig.USERS_TABLE
    users_col_username = sqlpasconfig.USERS_COL_USERNAME
    users_col_password = sqlpasconfig.USERS_COL_PASSWORD

    def __init__(self, id, title=None, connection=None):
        self._id = self.id = id
        self.title = title
        self._connection = connection
        # Update the SafeSQLQuery objects
        self.manage_changeProperties()

    def manage_changeProperties(self, **kwargs):
        """Ensure the SQL methods get regenerated."""
        self.delSQLQueries()
        PropertyManager.manage_changeProperties(self, **kwargs)
        self.addSQLQueries()

    def manage_editProperties(self, REQUEST):
        """Ensure the SQL methods get regenerated."""
        self.delSQLQueries()
        res = PropertyManager.manage_editProperties(self, REQUEST)
        self.addSQLQueries()
        return res

    security.declarePrivate('delSQLQueries')
    def delSQLQueries(self):
        """Remove the previous SafeSQLQuery instances."""
        sqllist = self.objectIds('Folder')
        self.manage_delObjects(ids=sqllist)

    security.declarePrivate('addSQLQueries')
    def addSQLQueries(self):
        """Add the new SafeSQLQuery instances."""
        oids = self.objectIds()
        for id, title, params, sql in self.getSQLQueries():
            sql = sql % self.getSchemaConfig()
            if id not in oids:
                o = SQL('query', title, self._connection, params, sql)
                self._setObject(id, SafeSQLQuery(id, o))

    security.declarePrivate('getSQLQueries')
    def getSQLQueries(self):
        """Return a tuple of queries.

        Each query has id, title, parameters and the query template
        to be used by addSQLQueries.
        """
        return ()

    security.declarePrivate('getSchemaConfig')
    def getSchemaConfig(self):
        """Return the dictionary schema config."""
        return {}

    security.declarePrivate('findMapping')
    def findMapping(self, key, reverse=False):
        """Returns the associated name for a given key.

        The mapping is stored in a property. The name of this property
        is given by the self.mapping value.

        Each line of the mapping should be in the format: key/map

        If the key matches a mapping, we return the map. When the reverse
        parameter is True, we return the key matched by a map.

        If the mapping is not found, we return the original key.
        """
        for line in self.getProperty(self.mapping, []):
            if reverse:
                if line.endswith('/'+key):
                    return line[:line.find('/')]
            else:
                if line.startswith(key+'/'):
                    return line[line.find('/')+1:]
        return key

    security.declarePrivate('remapKeys')
    def remapKeys(self, data, reverse=False):
        """Remaps the keys from a given dictionary."""
        res = {}
        for key, value in data.items():
            mapping = self.findMapping(key, reverse)
            res[mapping] = value
        return res
