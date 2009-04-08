"""Initialize CMFDiffTool Product"""

import sys
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
from Products.CMFCore.permissions import AddPortalContent

import Products.CMFDiffTool.CMFDiffTool
import Products.CMFDiffTool.FieldDiff
import Products.CMFDiffTool.TextDiff
import Products.CMFDiffTool.ListDiff
import Products.CMFDiffTool.BinaryDiff
import Products.CMFDiffTool.ChangeSet
import Products.CMFDiffTool.CMFDTHtmlDiff
import Products.CMFDiffTool.ATCompoundDiff

this_module = sys.modules[ __name__ ]
product_globals = globals()
tools = ( CMFDiffTool.CMFDiffTool,)

contentConstructors = (ChangeSet.manage_addChangeSet,)
contentClasses = (ChangeSet.ChangeSet,)

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())
registerDirectory('skins/ChangeSet', globals())

CMFDiffTool.registerDiffType(BinaryDiff.BinaryDiff)
CMFDiffTool.registerDiffType(FieldDiff.FieldDiff)
CMFDiffTool.registerDiffType(ListDiff.ListDiff)
CMFDiffTool.registerDiffType(TextDiff.TextDiff)
CMFDiffTool.registerDiffType(CMFDTHtmlDiff.CMFDTHtmlDiff)
CMFDiffTool.registerDiffType(ATCompoundDiff.ATCompoundDiff)

def initialize(context):
    utils.ToolInit('CMF Diff Tool',
                    tools = tools,
                    icon='tool.gif' 
                    ).initialize( context )

    utils.ContentInit(ChangeSet.ChangeSet.meta_type,
                      content_types = contentClasses,
                      extra_constructors = contentConstructors,
                      permission = AddPortalContent).initialize(context)
