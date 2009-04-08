PROJECTNAME = 'SQLPASPlugin'
GLOBALS = globals()

USERS_TABLE = 'users'
USERS_COL_USERNAME = 'username'
USERS_COL_PASSWORD = 'password'

ROLES_TABLE = 'roles'
ROLES_COL_USERNAME = 'username'
ROLES_COL_ROLENAME = 'rolename'

USERMANAGER_ID = 'source_users'
ROLEMANAGER_ID = 'source_roles'
PROPERTYPROVIDER_ID = 'source_properties'

# If you use reserved names as fieldnames, you probably need
# to use a wrap char here, e.g.: '"'
WRAPCHAR = ''

# Cache of user passwords will make authentication of users considerably
# faster. This is important for Plone 2.5 and older which use a session
# cookie containing the users login name and password and need to verify
# the password on every request. If you are using Plone 3.0 and later or
# an older Plone with a different session manager (such as SessionCrumbler)
# this should have little effect. 
CACHE_PASSWORDS = False
