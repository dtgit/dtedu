from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass

from Products.PlonePAS.interfaces.group import IGroupManagement
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.PluggableAuthService.utils import classImplements

from Products.SQLPASPlugin.plugins.sql import SQLBase


manage_addSQLGroupManagerForm = DTMLFile('../zmi/GroupManagerForm', globals())

def manage_addSQLGroupManager(self, id, title='', sql_connection='', REQUEST=None):
    """Add a SQLGroupManager to a Pluggable Auth Service.
    """
    rm = SQLGroupManager(id, title, sql_connection)
    self._setObject(rm.getId(), rm)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'SQLGroupManager+added.'
                            % self.absolute_url())

class SQLGroupManager(SQLBase):

    meta_type = 'SQL Group Manager'
    security = ClassSecurityInfo()

    #
    # IGroupsPlugin implementation
    #
    security.declarePrivate('getGroupsForPrincipal')
    def getGroupsForPrincipal(self, principal, request=None ):

        """ principal -> ( group_1, ... group_N )

        o Return a sequence of group names to which the principal
          (either a user or another group) belongs.

        o May assign groups based on values in the REQUEST object, if present
        """
        pass

    #
    # IGroupManagement implementation
    #
    def addGroup(self, sel, id, **kw):
        """
        Create a group with the supplied id, roles, and groups.
        return True if the operation suceeded
        """
        pass

    def addPrincipalToGroup(self, principal_id, group_id):
        """
        Add a given principal to the group.
        return True on success
        """
        pass

    def updateGroup(self, id, **kw):
        """
        Edit the given group. plugin specific
        return True on success
        """
        pass

    def setRolesForGroup(self, group_id, roles=()):
        """
        Set roles for group
        return True on success
        """
        pass

    def removeGroup(self, group_id):
        """
        Remove the given group
        return True on success
        """
        pass

    def removePrincipalFromGroup(self, principal_id, group_id):
        """
        Remove the given principal from the group
        return True on success
        """
        pass


classImplements(SQLGroupManager,
                IGroupManagement,
                IGroupsPlugin)

InitializeClass(SQLGroupManager)
