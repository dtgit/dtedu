##############################################################################
#
# Cocommpyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Kupu Plone integration

This package is a python package and contains a filesystem-based skin
layer containing the necessary UI customization to integrate Kupu as a
wysiwyg editor in Plone.

$Id: __init__.py 39356 2007-02-24 14:38:50Z wiggy $
"""
from App.Common import package_home
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
from Products.kupu.plone.plonelibrarytool import PloneKupuLibraryTool
from Products.kupu import kupu_globals

try:
    from Products.GenericSetup import profile_registry
    from Products.GenericSetup import BASE, EXTENSION
    from Products.CMFPlone.interfaces import IPloneSiteRoot
except ImportError:
    profile_registry = None

registerDirectory('plone/kupu_plone_layer', kupu_globals)
registerDirectory('plone/kupu_references', kupu_globals)
registerDirectory('tests', kupu_globals)

def initialize(context):
    try:
        init = utils.ToolInit("kupu Library Tool",
                       tools=(PloneKupuLibraryTool,),
                       icon="kupu_icon.gif",
                       )
    except TypeError:
        # Try backward compatible form of the initialisation call
        init = utils.ToolInit("kupu Library Tool",
                       tools=(PloneKupuLibraryTool,),
                       product_name='kupu',
                       icon="kupu_icon.gif",
                       )
    init.initialize(context)

    if profile_registry is not None:
        profile_registry.registerProfile('default',
                                     'Kupu',
                                     'Extension profile for Kupu',
                                     'plone/profiles/default',
                                     'kupu',
                                     EXTENSION,
                                     for_=IPloneSiteRoot)

