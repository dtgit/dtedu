from Products.SQLPASPlugin import config

# The possible values for TESTING_DB are: "sqlite", "postgresql" and "mysql"

# MySQL
#TESTING_DB = 'mysql'
#TESTING_DB_EXTRA = "pas_test zope zope"

# PostgreSQL
#TESTING_DB = 'postgresql'
#TESTING_DB_EXTRA = "dbname=pas_test user=zope password=zope host=localhost"

# SQLite
TESTING_DB = 'sqlite'
TESTING_DB_EXTRA = ''

# This is currently only used for the automated tests.
# Changing these values has no effect whatsoever.
TESTING_USERS_COLUMNS = (
    (config.USERS_COL_USERNAME, 'varchar', 20, 'primary key'),
    (config.USERS_COL_PASSWORD, 'varchar', 40, ''),
    ('firstname', 'varchar', 20, ''),
    ('lastname', 'varchar', 20, ''),
    ('email', 'varchar', 50, ''),
    ('date_created', 'datetime', None, ''),
    ('date_updated', 'datetime', None, ''),
)
TESTING_ROLES_COLUMNS = (
    (config.ROLES_COL_USERNAME, 'varchar', 20, ''),
    (config.ROLES_COL_ROLENAME, 'varchar', 20, ''),
)
TESTING_USERS_TABLE = 'test_pas_users'
TESTING_ROLES_TABLE = 'test_pas_roles'
