from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "SimpleAttachment"
GLOBALS = globals()
DEFAULT_ADD_CONTENT_PERMISSION = "Add Attachment"

setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner',))