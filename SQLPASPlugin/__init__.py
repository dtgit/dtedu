from AccessControl.Permissions import add_user_folders
from Products.CMFCore.DirectoryView import registerDirectory
from Products.PluggableAuthService import registerMultiPlugin

from plugins import propertyprovider, usermanager, rolemanager
import config as sqlpasconfig

from Extensions import *

try:
    registerMultiPlugin(propertyprovider.SQLPropertyProvider.meta_type)
    registerMultiPlugin(usermanager.SQLUserManager.meta_type)
    registerMultiPlugin(rolemanager.SQLRoleManager.meta_type)

except RuntimeError:
    # make refresh users happy
    pass

def initialize(context):

    context.registerClass(propertyprovider.SQLPropertyProvider,
                          permission = add_user_folders,
                          constructors = (
                              propertyprovider.manage_addSQLPropertyProviderForm,
                              propertyprovider.manage_addSQLPropertyProvider),
                          visibility = None,
                          icon='zmi/sql.jpg'
                          )
    context.registerClass(usermanager.SQLUserManager,
                          permission = add_user_folders,
                          constructors = (
                              usermanager.manage_addSQLUserManagerForm,
                              usermanager.manage_addSQLUserManager),
                          visibility = None,
                          icon='zmi/sql.jpg'
                          )
    context.registerClass(rolemanager.SQLRoleManager,
                          permission = add_user_folders,
                          constructors = (
                              rolemanager.manage_addSQLRoleManagerForm,
                              rolemanager.manage_addSQLRoleManager),
                          visibility = None,
                          icon='zmi/sql.jpg'
                          )
