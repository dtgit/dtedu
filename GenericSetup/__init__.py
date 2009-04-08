""" GenericSetup product initialization.

$Id: __init__.py 81996 2007-11-27 21:46:16Z yuppie $
"""

from AccessControl import ModuleSecurityInfo

from interfaces import BASE, EXTENSION
from permissions import ManagePortal
from registry import _profile_registry as profile_registry

security = ModuleSecurityInfo('Products.GenericSetup')
security.declareProtected(ManagePortal, 'profile_registry')

def initialize(context):

    import tool

    context.registerClass(tool.SetupTool,
                          constructors=(#tool.addSetupToolForm,
                                        tool.addSetupTool,
                                        ),
                          permissions=(ManagePortal,),
                          interfaces=None,
                          icon='www/tool.png',
                         )

# BBB: for setup tools created with CMF 1.5 if CMFSetup isn't installed
try:
    import Products.CMFSetup
except ImportError:
    import bbb
    import bbb.registry
    import bbb.tool

    __module_aliases__ = (('Products.CMFSetup', bbb),
                          ('Products.CMFSetup.registry', bbb.registry),
                          ('Products.CMFSetup.tool', bbb.tool))
