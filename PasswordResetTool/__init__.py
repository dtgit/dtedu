"""Initialize PasswordResetTool Product"""

import sys
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
import PasswordResetTool

this_module = sys.modules[ __name__ ]

product_globals = globals()

tools = ( PasswordResetTool.PasswordResetTool, )

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/PasswordReset', globals())

def initialize(context):
    utils.ToolInit('Password Reset Tool',
                    tools = tools,
                    icon='tool.gif' 
                    ).initialize( context )
