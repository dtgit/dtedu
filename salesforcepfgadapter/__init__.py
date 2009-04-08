from AccessControl import ModuleSecurityInfo
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.salesforcepfgadapter.config import PROJECTNAME, GLOBALS, \
    SFA_ADD_CONTENT_PERMISSION
from Products.PloneFormGen.config import ADD_CONTENT_PERMISSION, SKINS_DIR

registerDirectory(SKINS_DIR + '/salesforcepfgadapter_images', GLOBALS)

def initialize(context):    

    import content

    ##########
    # Add our content types
    # A little different from the average Archetype product
    # due to the need to individualize some add permissions.
    #
    # This approach borrowed from ATContentTypes
    #
    listOfTypes = listTypes(PROJECTNAME)

    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        
        if atype.portal_type == 'SalesforcePFGAdapter':
            permission = SFA_ADD_CONTENT_PERMISSION
        else:
            permission = ADD_CONTENT_PERMISSION
        
        utils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permission,
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

    ModuleSecurityInfo('Products.PloneFormGen').declarePublic('SalesforcePFGAdapterMessageFactory')
    ModuleSecurityInfo('Products.PloneFormGen').declarePublic('HAS_PLONE25')

# Import "PloneFormGenMessageFactory as _" to create message ids
# in the ploneformgen domain
# Zope 3.1-style messagefactory module
# BBB: Zope 2.8 / Zope X3.0
try:
    from zope.i18nmessageid import MessageFactory
except ImportError:
    from messagefactory_ import SalesforcePFGAdapterMessageFactory
else:
    SalesforcePFGAdapterMessageFactory = MessageFactory('salesforcepfgadapter')

# Check for Plone versions
try:
    from Products.CMFPlone.migrations import v2_5
except ImportError:
    HAS_PLONE25 = False
else:
    HAS_PLONE25 = True
try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    HAS_PLONE30 = False
else:
    HAS_PLONE30 = True
