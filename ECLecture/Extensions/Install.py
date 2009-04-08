# -*- coding: utf-8 -*-
# $Id: Install.py,v 1.5 2006/09/05 17:08:26 mxp Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.

from StringIO import StringIO

from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Archetypes.public import listTypes
from Products.CMFCore.utils import getToolByName

# local imports
from Products.ECLecture.config import *
from Products.ECLecture.Extensions.Migrations import migrate

def addCatalogIndex(self, out, catalog, index, type, extra=None):
    """Add the given index name, of the given type, to the catalog."""
    if index not in catalog.indexes():
        catalog.addIndex(index, type, extra)
        print >> out, "Added index", index, "to catalog"
    else:
        print >> out, "Index", index, "already in catalog"

def addCatalogMetadata(self, out, catalog, column):
    """Add the given column to the catalog's metadata schema"""
    if column not in catalog.schema():
        catalog.addColumn(column)
        print >> out, "Added", column, "to catalog metadata"
    else:
        print >> out, column, "already in catalog metadata"

def removeCatalogMetadata(self, out, catalog, column):
    """Delete the given metadata column"""
    # QueueCatalog work-around
    if catalog.meta_type == 'ZCatalog Queue':
         catalog = self.unrestrictedTraverse(catalog._location)
    if column in catalog.schema():
        catalog.delColumn(column)
        print >> out, "Removed column", column
    else:
        print >> out, "Column", column, "not in catalog"


def installDependencies(self, out):
    """
    Checks wether or not depending products are installed. 
    If not, try to install them.
    """
    qi = getToolByName(self, 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if (qi.isProductInstallable(product)) and (not qi.isProductInstalled(product)):
            qi.installProduct(product)


def setupTool(self, out):
    """ 
    Add the tool to the portal root folder.
    """
    pass

def removeTool(self):
    """
    Remove the tool from the portal root folder.
    """
    pass


def setupCatalog(self, out, reinstall):
    catalog = getToolByName(self, 'portal_catalog')
    addCatalogMetadata(self, out, catalog, 'getTimePeriod')
    addCatalogIndex(self, out, catalog, 'getTimePeriod', 'FieldIndex')

def cleanCatalog(self, out, reinstall):
    catalog = getToolByName(self, 'portal_catalog')
    if not reinstall:
        removeCatalogMetadata(self, out, catalog, 'getTimePeriod')


def addPrefsPanel(self, out):
    """
    Add the tool to Plone's preferences panel.
    """
    pass


def removePrefsPanel(self):
    """
    Remove the tool from Plone's preferences panel.
    """
    pass
    

def setWorkflow(self, out):
    """
    Add workflow.
    """
    pass


def install(self, reinstall=False):
    """
    Installs the product.
    """
    out = StringIO()

    # install depending products
    installDependencies(self, out)

    # install types
    installTypes(self, out, listTypes(PRODUCT_NAME), PRODUCT_NAME)

    # install subskins
    install_subskin(self, out, GLOBALS)

    # install workflows
    setWorkflow(self, out)

    # install tools
    setupTool(self, out)

    # setup catalog metadata
    setupCatalog(self, out, reinstall)

    # register tool to preferences panel
    addPrefsPanel(self, out)

    # enable portal_factory for given types
    factory_tool = getToolByName(self, 'portal_factory')
    factory_types=[
        ECL_NAME,
        ] + factory_tool.getFactoryTypes().keys()
    factory_tool.manage_setPortalFactoryTypes(listOfTypeIds=factory_types)

    # register a custom view for folders
    portal_types = getToolByName(self, 'portal_types')
    folderFTI = portal_types.Folder
    try:
        if 'folder_lectures_view' not in folderFTI.view_methods:
            folderFTI.view_methods += ('folder_lectures_view',)
            print >> out, "Added new view template for folders."
    except:
        print >> out, "Adding new view template for folders failed."

    # Run migrations
    #if RUN_MIGRATIONS:
    print >> out, migrate(self)

    print >> out, "Successfully installed %s." % PRODUCT_NAME
    return out.getvalue()


def uninstall(self, reinstall=False):
    """ 
    Uninstalls the product.
    """
    out = StringIO()

    # remove metadata from catalog
    cleanCatalog(self, out, reinstall)

    # remove tool from prefs panel
    removePrefsPanel(self)

    # remove tool from portal root
    removeTool(self)

    # remove custom view for folders
    portal_types = getToolByName(self, 'portal_types')
    folderFTI = portal_types.Folder
    try:
        if 'folder_lectures_view' in folderFTI.view_methods:
            source = folderFTI.view_methods
            views = []
            for view in source:
                if view not in ('folder_lectures_view',):
                    views.append(view)
            folderFTI.manage_changeProperties(view_methods=tuple(views))
            print >> out, "Removed view template from folder."
    except:
        print >> out, "Removing view template from folder failed."

    print >> out, "Successfully uninstalled %s." % PRODUCT_NAME
    return out.getvalue()
