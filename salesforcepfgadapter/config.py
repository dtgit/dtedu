from Products.CMFCore.permissions import setDefaultRoles

## The Project Name
PROJECTNAME = "salesforcepfgadapter"

## The skins dir
SKINS_DIR = 'skins'

## Globals variable
GLOBALS = globals()

## Permission for creating a SalesforcePFGAdapter
SFA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Salesforce PFG Adapter'
setDefaultRoles(SFA_ADD_CONTENT_PERMISSION, ('Manager','Owner',))

## Required field marker
REQUIRED_MARKER = "(required)"

## Used by homegrown, lightweight migration infrastructure
KNOWN_VERSIONS = (
    '1.0alpha1',
    '1.0alpha2',
    '1.0alpha3',
    '1.0rc1',
    '1.0rc2',
)