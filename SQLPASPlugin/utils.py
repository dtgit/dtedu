__author__  = '''Rocky Burt <rocky@serverzen.com>'''
__docformat__ = 'plaintext'

__all__ = ('log', 'logEx', 'updatePAS')

import logging
from Products.SQLPASPlugin import config

logger = logging.getLogger('SQLPASPlugin')

def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s \n%s', summary, message)

def logEx(message='', summary='', severity=logging.ERROR):
    logger.log(severity, '%s \n%s', summary, message)

def _debug(msg, out):
    if out:
        print >> out, msg
    log(msg)

def updatePAS(context, sql_connection, out=None):
    """This method retrieves the current context's acl_users, ensures
    that it is indeed a PAS instance, and then goes ahead and sets
    up SQLPASPlugin in that PAS instance (if it is actually a PAS instance).
    """

    uf = context.acl_users
    if uf.meta_type == 'Pluggable Auth Service':
        factory = uf.manage_addProduct['SQLPASPlugin']
        if out:
            print >> out, "Found pluggable auth service instance"

        # Setup the SQLUserManager PAS plugin
        usersId = config.USERMANAGER_ID
        if usersId in uf.objectIds():
            if out:
                print >> out, 'Deleting "%s"...' % usersId
            uf.manage_delObjects([usersId])
        factory.manage_addSQLUserManager(id=usersId,
                                         sql_connection=sql_connection)
        plugin = uf[usersId]
        plugin.manage_activateInterfaces(['IAuthenticationPlugin',
                                          'IUserEnumerationPlugin',
                                          'IUserManagement',
                                          'IUserAdderPlugin'])

        # Setup the SQLRoleManager PAS plugin
        rolesId = config.ROLEMANAGER_ID
        if rolesId in uf.objectIds():
            if out:
                print >> out, 'Deleting "%s"...' % rolesId
            uf.manage_delObjects([rolesId])
        factory.manage_addSQLRoleManager(id=rolesId,
                                         sql_connection=sql_connection)
        plugin = uf[rolesId]
        plugin.manage_activateInterfaces(['IRoleAssignerPlugin',
                                          'IRolesPlugin'])

        # Setup the SQLPropertyManager PAS plugin
        propsId = config.PROPERTYPROVIDER_ID
        if propsId in uf.objectIds():
            if out:
                print >> out, 'Deleting "%s"...' % propsId
            uf.manage_delObjects([propsId])
        factory.manage_addSQLPropertyProvider(id=propsId,
                                              sql_connection=sql_connection)
        plugin = uf[propsId]
        plugin.manage_activateInterfaces(['IPropertiesPlugin',
                                          'IUpdatePlugin'])

    else:
        if out:
            print >> out, "Didn't find a pluggable auth service instance"
