##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Install kupu in CMF and, if available, Plone

This is best executed using CMFQuickInstaller

$Id: Install.py 39571 2007-02-28 13:34:03Z fschulze $
"""
import os.path
import sys
import re
from StringIO import StringIO

from App.Common import package_home

from Products.CMFCore.utils import getToolByName, minimalpath
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.kupu import kupu_globals
from Products.kupu.plone.util import register_layer, unregister_layers
from Products.kupu.plone import util
from Products.kupu.config import TOOLNAME, PROJECTNAME, TOOLTITLE
from OFS.ObjectManager import BadRequestException
from zExceptions import BadRequest

try:
    from Products.MimetypesRegistry import MimeTypeItem
except ImportError:
    pass # Plone not available

kupu_package_dir = package_home(kupu_globals)

def install_plone(self, out):
    """Install with plone
    """
    # register the plone skin layers
    register_layer(self, 'plone/kupu_plone_layer', 'kupu_plone', out)
    # By default, add the directory view but not the skin layer for the reference browser
    register_layer(self, 'plone/kupu_references', 'kupu_references', out, add=False)
    register_layer(self, 'tests', 'kupu_tests', out)

    # register as editor
    portal_props = getToolByName(self, 'portal_properties')
    site_props = getattr(portal_props,'site_properties', None)
    attrname = 'available_editors'
    if site_props is not None:
        editors = list(site_props.getProperty(attrname)) 
        if 'Kupu' not in editors:
            editors.append('Kupu')
            site_props._updateProperty(attrname, editors)        
            print >>out, "Added 'Kupu' to available editors in Plone."
    install_libraries(self, out)
    install_configlet(self, out)
    install_transform(self, out)
    install_resources(self, out)
    install_customisation(self, out)

def _read_resources():
    resourcefile = open(os.path.join(kupu_package_dir, 'plone', 'head.kupu'), 'r')
    try:
        data = resourcefile.read()
        return data
    finally:
        resourcefile.close()

def css_files(resources):
    CSSPAT = re.compile(r'\<link [^>]*rel="stylesheet"[^>]*\${portal_url}/([^"]*)"')
    for m in CSSPAT.finditer(resources):
        id = m.group(1)
        yield id

def js_files(resources):
    JSPAT = re.compile(r'\<script [^>]*\${portal_url}/([^"]*)"')
    for m in JSPAT.finditer(resources):
        id = m.group(1)
        if id=='sarissa.js':
            continue
        yield id

def install_resources(self, out):
    """Add the js and css files to the resource registry so that
    they can be merged for download.
    """
    try:
        from Products.ResourceRegistries.config import CSSTOOLNAME, JSTOOLNAME
    except ImportError:
        print >>out, "Resource registry not found: kupu will load its own resources"
        return

    data = _read_resources()
    
    CONDITION = '''python:portal.kupu_library_tool.isKupuEnabled(REQUEST=request)'''
    csstool = getToolByName(self, CSSTOOLNAME, None)
    jstool = getToolByName(self, JSTOOLNAME, None)
    if csstool is None or jstool is None:
        return

    for id in css_files(data):
        print >>out, "CSS file", id
        cookable = True
        csstool.manage_removeStylesheet(id=id)
        csstool.manage_addStylesheet(id=id,
            expression=CONDITION,
            rel='stylesheet',
            enabled=True,
            cookable=cookable)

    existing = [ sheet.getId() for sheet in jstool.getResources()]
    if 'kupucontextmenu.js' in existing:
        jstool.manage_removeScript('kupucontextmenu.js');
    # Insert sarissa.js into the scripts but only if it isn't already
    # there.
    SARISSA = 'sarissa.js'
    if SARISSA not in existing:
        jstool.manage_addScript(id=SARISSA, enabled=True,
            cookable=True,
            compression='safe',
            cacheable=True)
        if 'plone_javascripts.js' in existing:
            jstool.moveResourceAfter(SARISSA, 'plone_javascripts.js')
        else:
            jstool.moveResourceToBottom(SARISSA)
        print >>out, "JS file", SARISSA

    for id in js_files(data):
        print >>out, "JS file", id
        jstool.manage_removeScript(id=id)
        jstool.manage_addScript(id=id,
            expression=CONDITION,
            enabled=True,
            compression='safe',
            cookable=True)

def uninstall_resources(self, out):
    """Remove the js and css files from the resource registries"""
    try:
        from Products.ResourceRegistries.config import CSSTOOLNAME, JSTOOLNAME
    except ImportError:
        return

    data = _read_resources()
    
    csstool = getToolByName(self, CSSTOOLNAME)
    jstool = getToolByName(self, JSTOOLNAME)

    for id in css_files(data):
        csstool.manage_removeStylesheet(id=id)

    for id in js_files(data):
        jstool.manage_removeScript(id=id)
    print >>out, "Resource files removed"
    
def install_libraries(self, out):
    """Install everything necessary to support Kupu Libraries
    """
    # add the library tool
    addTool = self.manage_addProduct['kupu'].manage_addTool
    try:
        addTool('Kupu Library Tool')
        print >>out, "Added the Kupu Library Tool to the plone Site"
    except BadRequest:
        print >>out, "Kupu library Tool already added"    
    except: # Older Zopes
        #heuristics for testing if an instance with the same name already exists
        #only this error will be swallowed.
        #Zope raises in an unelegant manner a 'Bad Request' error
        e=sys.exc_info()
        if e[0] != 'Bad Request':
            raise
        print >>out, "Kupu library Tool already added"    

def install_configlet(self, out):
    try:
        portal_conf=getToolByName(self,'portal_controlpanel')
    except AttributeError:
        print >>out, "Configlet could not be installed"
        return
    try:
        portal_conf.registerConfiglet( 'kupu'
               , TOOLTITLE
               , 'string:${portal_url}/%s/kupu_config' % TOOLNAME
               , ''                 # a condition   
               , 'Manage portal'    # access permission
               , 'Plone'            # category to which kupu should be added: 
                                    # (Plone,Products,Members) 
               , 1                  # visibility
               , PROJECTNAME
               , 'kupuimages/kupu_icon.gif' # icon in control_panel
               , 'Kupu Library Tool'
               , None
               )
    except KeyError:
        pass # Get KeyError when registering duplicate configlet.

def install_transform(self, out):
    try:
        util.install_transform(self)
        util.remove_transform(self) # Transform is installed but disabled by default.
    except (NameError,AttributeError):
        print >>out, "Transform not installed."

def install_customisation(self, out):
    """Default settings may be stored in a customisation policy script so
    that the entire setup may be 'productised'"""

    # Skins are cached during the request so (in case new skin
    # folders have just been added) we need to force a refresh of the
    # skin.
    self.changeSkin(None)

    scriptname = '%s-customisation-policy' % PROJECTNAME.lower()
    cpscript = getattr(self, scriptname, None)
    # If the user hasn't created a CP then use the sample.
    if not cpscript:
        cpscript = getattr(self, 'sample-kupu-customisation-policy', None)
    if cpscript:
        cpscript = cpscript.__of__(self)

    if cpscript:
        print >>out,"Customising %s" % PROJECTNAME
        print >>out,cpscript()
    else:
        print >>out,"No customisation policy"

def install(self):
    out = StringIO()

    # register the core layer
    register_layer(self, 'common', 'kupu', out)

    # try for plone
    try:
        import Products.CMFPlone
    except ImportError:
        pass
    else:
        install_plone(self, out)

    print >>out, "kupu successfully installed"
    return out.getvalue()

def uninstall_transform(self, out):
    transform_tool = getToolByName(self, 'portal_transforms')
    try:
        util.remove_transform(self)
        transform_tool.manage_delObjects(['html-to-captioned', 'captioned-to-html'])
    except:
        print >>out, "Transform not removed"
        pass
    else:
        print >>out, "Transform removed"

def uninstall_tool(self, out):
    try:
        self.manage_delObjects([TOOLNAME])
    except:
        pass
    else:
        print >>out, "Kupu tool removed"

def uninstall(self):
    out = StringIO()

    # remove the configlet from the portal control panel
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        configTool.unregisterConfiglet('kupu')
        out.write('Removed kupu configlet\n')

    uninstall_transform(self, out)
    uninstall_tool(self, out)
    uninstall_resources(self, out)
    unregister_layers(self, ['kupu_plone', 'kupu_references', 'kupu'], out)

    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
