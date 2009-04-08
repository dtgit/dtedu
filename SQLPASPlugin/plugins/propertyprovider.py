# This module was inspired by MySQLPropPlugin

import types

from Globals import DTMLFile
from Globals import InitializeClass
from Persistence import Persistent
from DateTime.DateTime import DateTime
from AccessControl import ClassSecurityInfo

from ZODB.POSException import ConflictError

from Products.ZSQLMethods.SQL import SQL
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.utils import createViewName
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PluggableAuthService.interfaces.plugins import IUpdatePlugin
from Products.PluggableAuthService.UserPropertySheet import _guessSchema

from Products.SQLPASPlugin.utils import logEx
from Products.SQLPASPlugin.plugins.sql import SQLBase
from Products.SQLPASPlugin.config import WRAPCHAR

from Products.PlonePAS.interfaces.plugins import IMutablePropertiesPlugin
from Products.PlonePAS.sheet import MutablePropertySheet


def manage_addSQLPropertyProvider(self, id, title='', sql_connection='',
                                  RESPONSE=None, schema=None, **kw):
    """Create an instance of a mutable property manager.
    """
    o = SQLPropertyProvider(id, title, sql_connection, schema, **kw)
    self._setObject(o.getId(), o)
    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')

manage_addSQLPropertyProviderForm = DTMLFile(
    "../zmi/MutablePropertyProviderForm", globals())

def _findAction(l, action):
    x = 0
    found = None
    while x < len(l) and found is None:
        if l[x]['action'] == action:
            found = l[x]
        x += 1
    return found


class SQLPropertyProvider(SQLBase):
    """Storage for mutable properties in SQL for users/groups.
    """
    meta_type = 'SQL Mutable Property Provider'
    security = ClassSecurityInfo()
    mapping = 'col_mapping'

    _properties = SQLBase._properties + (
        {'id':'col_mapping', 'type': 'lines', 'mode': 'w'},
        {'id': 'only_for_matches', 'type': 'boolean', 'mode': 'w',
         'label': 'Only return properties when there is a match'},
    )

    col_mapping = ()
    only_for_matches = False

    def __init__(self, id, title='', connection='', schema=None, **kw):
        """Create SQL mutable property provider.

        Provide a schema either as a list of (name,type,value) tuples
        in the 'schema' parameter or as a series of keyword parameters
        'name=value'. Types will be guessed in this case.

        The 'value' is meant as the default value, and will be used
        unless the user provides data.

        If no schema is provided by constructor, the properties of the
        portal_memberdata object will be used.

        Types available: string, text, boolean, int, long, float, lines, date
        """
        # Calculate schema and default values
        defaultvalues = {}
        if not schema and not kw:
            schema = ()
        elif not schema and kw:
            schema = _guessSchema(kw)
            defaultvalues = kw
        else:
            schema = [(name, type) for name, type, value in schema]
            valuetuples = [(name, value) for name, type, value in schema]
            for name, value in valuetuples:
                defaultvalues[name] = value
        self._schema = tuple(schema)
        self._defaultvalues = defaultvalues
        SQLBase.__init__(self, id, title, connection)

    def __setstate__(self, state):
        Persistent.__setstate__(self, state)
        self.addSQLQueries()

    def _getSchema(self, isgroup=None):
        # This could probably stand to be cached
        datatool = isgroup and "portal_groupdata" or "portal_memberdata"
        schema = self._schema
        if not schema:
            # if no schema is provided, use portal_memberdata properties
            schema = ()
            #mdtool = getToolByName(self, datatool)
            #mdschema = mdtool.propertyMap()
            #schema = [(elt['id'], elt['type']) for elt in mdschema]
        return schema

    def _getDefaultValues(self, isgroup=None):
        """Returns a dictionary mapping of property names to default values.
        Defaults to portal_*data tool if necessary.
        """
        datatool = isgroup and "portal_groupdata" or "portal_memberdata"
        defaultvalues = self._defaultvalues
        if not self._schema:
            # if no schema is provided, use portal_*data properties
            defaultvalues = {}
            #mdtool = getToolByName(self, datatool)
            # we rely on propertyMap and propertyItems mapping
            #mdvalues = mdtool.propertyItems()
            #for name, value in mdvalues:
            #    defaultvalues[name] = value
        return defaultvalues

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
    # IPropertiesPlugin implementation
    #
    def getPropertiesForUser(self, user, request=None):
        """Get property values for a user or group.

        Returns a dictionary of values or a PropertySheet.
        """

        view_name = createViewName('getPropertiesForUser', user.getUserName())
        cached_info = self.ZCacheable_get(view_name=view_name)
        if cached_info is not None:
            return MutablePropertySheet(self.id, **cached_info)

        isGroup = getattr(user, 'isGroup', lambda: None)()
        try:
            res = self.sqlLoadProperties(username=user.getUserName())
            all = res.dictionaries()
            if len(all) > 0:
                data = all[0]
                del data[self.getProperty('users_col_username')]
                del data[self.getProperty('users_col_password')]
                # Remove 'id' column if it exists in database result set
                if data.get('id', None):
                    del data['id']
            elif self.only_for_matches:
                return None
            else:
                data = {}
        except ConflictError:
            raise
        except:
            data = {}
            logEx("Error while trying to load properties for user")

        items = data.items()
        for key, value in items:
            _type = type(value)
            if value is None:
                value = ''
                data[key] = value
            elif str(_type).lower().startswith("<type 'date"):
                value = DateTime(str(value))
                data[key] = value

        data = self.remapKeys(data)
        defaults = self._getDefaultValues(isGroup)

        # Convert from the generic db representation to the correct type
        for name, property_type in self._getSchema(isGroup) or ():
            if name in data.keys():
                if property_type == 'string' or property_type == 'text':
                    continue
                elif property_type == 'int':
                    data[name] = int(data[name])
                elif property_type == 'float':
                    data[name] = float(data[name])
                elif property_type == 'long':
                    data[name] = long(data[name])
                elif property_type == 'boolean':
                    if data[name] == '1':
                        data[name] = 1
                    else:
                        data[name] = 0
                elif property_type == 'date':
                    data[name] = DateTime(data[name])
                elif property_type == 'lines':
                    data[name] = tuple(data[name])
                else:
                    raise ValueError, 'Property %s: unknown type' % property_type

        # Provide default values where missing
        if not data:
            data = {}
        for key, val in defaults.items():
            if not data.has_key(key):
                data[key] = val

        self.ZCacheable_set(data, view_name=view_name)

        sheet = MutablePropertySheet(self.id, **data)
        return sheet

    #
    # IMutablePropertiesPlugin implementation
    #
    def setPropertiesForUser(self, user, propertysheet):
        """Set the properties of a user or group based on the contents of a
        property sheet.
        """
        isGroup = getattr(user, 'isGroup', lambda: None)()
        props = dict(propertysheet.propertyItems())
        self.updateUserInfo(user, set_id=None, set_info=props)

    def deleteUser(self, user_id):
        """Remove properties stored for a user."""
        pass

    #
    # IUpdatePlugin implementation
    #
    def updateUserInfo(self, user, set_id, set_info):
        if set_id is not None:
            raise NotImplementedError, "Cannot currently rename the user id of a user"

        users_table = self.getProperty('users_table')
        users_col_username = self.getProperty('users_col_username')

        realFields = self.remapKeys(set_info, reverse=True)

        sql = 'UPDATE %s SET ' % users_table
        for key, value in realFields.items():
            _type = 'string'
            if type(value) == types.FloatType:
                _type = 'float'
            elif type(value) == types.IntType:
                _type = 'int'

            sql += ('%s' % WRAPCHAR) + key + '%s=<dtml-sqlvar %s type=%s>,' % (WRAPCHAR, key, _type)
        sql = sql[:-1]
        sql += " WHERE %s='%s'" % (users_col_username, user.getUserName())

        params = ' '.join(realFields.keys())
        sqlMethod = SQL('query', 'Update user info', self._connection, params, sql)
        sqlMethod = sqlMethod.__of__(self)

        data = dict(realFields)
        data[users_col_username] = user.getUserName()

        sqlMethod(**data)

        view_name = createViewName('getPropertiesForUser', user.getUserName())
        cached_info = self.ZCacheable_invalidate(view_name=view_name)


classImplements(SQLPropertyProvider,
                IPropertiesPlugin,
                IUpdatePlugin,
                IMutablePropertiesPlugin)

InitializeClass(SQLPropertyProvider)

_SQL_QUERIES = (
    (
     "sqlLoadProperties",
     "Load member properties",
     "username",
     """
SELECT *
FROM %(users_table)s
WHERE <dtml-sqltest username column="%(username_col)s" op="eq" type="string">
     """
    ),

)
