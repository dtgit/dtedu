from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass

from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.PluggableAuthService.interfaces.plugins import IRoleAssignerPlugin
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.utils import createViewName

from Products.SQLPASPlugin.plugins.sql import SQLBase
from Products.SQLPASPlugin import config as sqlpasconfig

manage_addSQLRoleManagerForm = DTMLFile('../zmi/RoleManagerForm', globals())


def manage_addSQLRoleManager(self, id, title='', sql_connection='', REQUEST=None):
    """Add a SQLRoleManager to a Pluggable Auth Service.
    """
    rm = SQLRoleManager(id, title, sql_connection)
    self._setObject(rm.getId(), rm)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'SQLRoleManager+added.'
                            % self.absolute_url())


class SQLRoleManager(SQLBase):
    """PAS plugin for managing roles in a SQL-based database.
    """
    meta_type = 'SQL Role Manager'
    security = ClassSecurityInfo()
    mapping = 'roles_mapping'

    _properties = (
        {'id':'roles_table', 'type': 'string', 'mode': 'w'},
        {'id':'roles_col_username', 'type': 'string', 'mode': 'w'},
        {'id':'roles_col_rolename', 'type': 'string', 'mode': 'w'},
        {'id':'roles_mapping', 'type': 'lines', 'mode': 'w'},
    )

    roles_mapping = ()
    roles_table = sqlpasconfig.ROLES_TABLE
    roles_col_username = sqlpasconfig.ROLES_COL_USERNAME
    roles_col_rolename = sqlpasconfig.ROLES_COL_ROLENAME

    #
    # SQLBase
    #
    security.declarePrivate('getSchemaConfig')
    def getSchemaConfig(self):
        return dict(roles_table=self.getProperty('roles_table'),
                    username_col=self.getProperty('roles_col_username'),
                    rolename_col=self.getProperty('roles_col_rolename'))

    security.declarePrivate('getSQLQueries')
    def getSQLQueries(self):
        return _SQL_QUERIES

    security.declareProtected(ManageUsers, 'assignRolesToPrincipal')
    def assignRolesToPrincipal(self, roles, principal_id):
        """Assign a specific set of roles, and only those roles, to a principal.

        o no return value
        o insert and delete roles on the SQL Backend based on the roles
          parameter
        """
        ignored_roles = ('Authenticated', 'Anonymous', 'Owner')
        roles = [role_id for role_id in roles if role_id not in ignored_roles]

        # Remove actual roles that are not in the roles parameter
        actual_roles = self.getRolesForPrincipal(principal_id)
        for role in actual_roles:
            if role not in roles:
                mapped = self.findMapping(role, reverse=True)
                self.sqlDelRoleForUser(username=principal_id, rolename=mapped)

        # Insert new roles
        for role in roles:
            if role not in ignored_roles:
                self.doAssignRoleToPrincipal(principal_id, role, _no_cache=True)

        view_name = createViewName('getRolesForPrincipal', principal_id)
        self.ZCacheable_invalidate(view_name)

    #
    # IRoleAssignerPlugin implementation
    #
    security.declarePrivate('doAssignRoleToPrincipal')
    def doAssignRoleToPrincipal(self, principal_id, role, _no_cache=False):
        """Create a principal/role association in the Role Manager.

        o Return a Boolean indicating whether the role was assigned or not
        """
        roles = self.getRolesForPrincipal(principal_id)
        if role in roles:
            return False
        mapped = self.findMapping(role, reverse=True)
        self.sqlAddRoleForUser(username=principal_id, rolename=mapped)

        if not _no_cache:
            view_name = createViewName('getRolesForPrincipal', principal_id)
            self.ZCacheable_invalidate(view_name)

        return True

    #
    # IRolesPlugin implementation
    #
    security.declarePrivate('getRolesForPrincipal')
    def getRolesForPrincipal(self, principal, request=None):
        """ principal -> ( role_1, ... role_N )
        o Return a sequence of role names which the principal has.
        o May assign roles based on values in the REQUEST object, if present.
        """
        view_name = createViewName('getRolesForPrincipal', principal)
        cached_info = self.ZCacheable_get(view_name)
        if cached_info is not None:
            return cached_info

        roles = []
        results = self.sqlRolesForUser(username=principal)
        for row in results.dictionaries():
            role = row.get('rolename')
            mapped = self.findMapping(role)
            roles.append(mapped)

        roles=tuple(roles)
        self.ZCacheable_set(roles, view_name)
        return roles


classImplements(SQLRoleManager,
                IRoleAssignerPlugin,
                IRolesPlugin)

InitializeClass(SQLRoleManager)

_SQL_QUERIES = (

    (
     "sqlRolesForUser",
     "Return the roles list for the user",
     "username",
     """
SELECT %(rolename_col)s as rolename
FROM %(roles_table)s
WHERE %(username_col)s=<dtml-sqlvar username type="string">
     """
    ),

    (
     "sqlAddRoleForUser",
     "Assign the role to the user",
     "username rolename",
     """
INSERT INTO %(roles_table)s (%(username_col)s, %(rolename_col)s)
VALUES (<dtml-sqlvar username type="string">,
        <dtml-sqlvar rolename type="string">)
     """
    ),

    (
     "sqlDelRoleForUser",
     "Remove the role from the user",
     "username rolename",
     """
DELETE FROM %(roles_table)s
WHERE %(username_col)s=<dtml-sqlvar username type="string">
AND   %(rolename_col)s=<dtml-sqlvar rolename type="string">
     """
    ),

)
