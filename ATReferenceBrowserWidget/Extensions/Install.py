from StringIO import StringIO
from Products.Archetypes.Extensions.utils import install_subskin
from Products.CMFCore.utils import getToolByName

from Products.ATReferenceBrowserWidget.config import *
        
def install(self):
    out = StringIO()
    
    # remove comments if you whish to install the demo type
    # installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    
    # install property for startup_directory
    props = getToolByName(self, "portal_properties").site_properties
    if not props.hasProperty('refwidget_startupdirectories'):
        props._setProperty('refwidget_startupdirectories', [], 'lines')
        out.write('Registered property refwidget_startupdirectories in site_properties - see readme.txt')

    install_subskin(self, out, GLOBALS)
    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()
