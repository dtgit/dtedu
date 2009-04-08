##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Kupu library tool setup handlers.
"""
import os

from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from Globals import InitializeClass
from Globals import package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.utils import CONVERTER
from Products.GenericSetup.utils import DEFAULT
from Products.GenericSetup.utils import ExportConfiguratorBase
from Products.GenericSetup.utils import ImportConfiguratorBase
from Products.GenericSetup.utils import KEY

try:
    from Products.CMFCore.permissions import ManagePortal
except ImportError:
    from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.PythonScripts.standard import Object

_pkgdir = package_home( globals() )
_xmldir = os.path.join( _pkgdir, 'xml' )

#
#   Configurator entry points
#
_FILENAME = 'kupu.xml'

def importKupuSettings(context):
    """ Import kupu settings from an XML file.
    """
    site = context.getSite()
    kupu = getToolByName(site, 'kupu_library_tool', None)
    if kupu is None:
        return 'Kupu: No tool!'

    body = context.readDataFile(_FILENAME)
    if body is None:
        return 'Kupu: Nothing to import.'

    # now act on the settings we've retrieved
    configurator = KupuToolImportConfigurator(site, 'utf-8')
    info = configurator.parseXML(body)

    config = info['config'][0]
    parastyles = config['parastyles']
    tableclasses = config['tableclasses']
    stylewhitelist = config['filterstyles']
    classblacklist = config['filterclasses']
    excludedhtml = [ (f['tags'].split(' '), f['attributes'].split(' ')) for f in config['filters']]
    
    captioning = config['captioning']
    userefbrowser = config['userefbrowser']
    linkbyuid = config['linkbyuid']
    filtersourceedit = config['filtersourceedit']
    installbeforeunload = config['installbeforeunload']

    kupu.configure_kupu(
        table_classnames = tableclasses,
        parastyles=parastyles,
        style_whitelist = stylewhitelist,
        class_blacklist = classblacklist,
        installBeforeUnload=installbeforeunload,
        linkbyuid=linkbyuid,
        captioning=captioning,
        )
    kupu.set_html_exclusions(excludedhtml)

    # Set up resources
    # XXX whitelist/blacklist handling
    resources = info['resources']
    types = kupu.zmi_get_resourcetypes()
    kupu.deleteResourceTypes([ t.name for t in types])
    for k in resources:
        kupu.addResourceType(k['id'], k['types'], k['mode'])
    kupu.setDefaultResource(info['defaultresource'][0])

    if info.has_key('generatepreviews'):
        # This code generates preview URLs automatically from the most
        # appropriately sized image (if you have PIL installed) or just an
        # image field (if you don't).
        #
        # If you have content types which don't always have an image, or if
        # this picks the wrong preview URL, you might want to change these
        # expressions.
        PREVIEW_EXPR = 'string:${object_url}/%s'
        PREVIEW = [ { 'portal_type': type,
            'expression': PREVIEW_EXPR % image,
            'normal': None,
            'scalefield': image.split('_',1)[0],
            } for (type, image) in kupu.getPreviewable() ]
        kupu.updatePreviewActions(PREVIEW)
    else:
        PREVIEW = []

    preview = PREVIEW + list(info['previews'])
    kupu.updatePreviewActions(preview)

    # Set up libraries
    libraries = info['libraries']
    deflib = info['defaultlibrary'][0]
    libs = kupu.zmi_get_libraries()
    kupu.deleteLibraries(range(len(libs)))
    for lib in libraries:
        kupu.addLibrary(**lib)
    kupu.zmi_set_default_library(deflib)

    
    toolbar = info['toolbar'][0]['elements']
    globaltoolbar = info['globaltoolbar'][0]
    kupu.set_toolbar_filters(toolbar, globaltoolbar)
    
    return 'Kupu settings imported.'

def exportKupuSettings(context):
    """ Export kupu settings as an XML file.
    """
    site = context.getSite()

    mhc = KupuToolExportConfigurator( site ).__of__( site )
    if mhc.getTool() is None:
        return 'Kupu not installed: no settings to export'

    text = mhc.generateXML()

    context.writeDataFile( _FILENAME, text, 'text/xml' )

    return 'Kupu settings exported.'


class KupuToolExportConfigurator(ExportConfiguratorBase):
    """ Synthesize XML description of cc properties.
    """
    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'getTool')
    def getTool(self):
        """Get Kupu's tool"""
        kupu = getToolByName(self._site, 'kupu_library_tool', None)
        return kupu

    def getPreviews(self):
        typetool = getToolByName(self._site, 'portal_types')
        kupu = self.getTool()
        typeinfos = typetool.listTypeInfo()
        previewable = [t for t in typeinfos if kupu.getPreviewForType(t.getId())]

        res = []
        for t in typeinfos:
            previewable = kupu.getPreviewForType(t.getId())
            if not previewable:
                continue
            portal_type =  t.getId()
            previewaction = kupu.getPreviewForType(portal_type)
            normalaction = kupu.getNormalViewForType(portal_type)
            scalefield = kupu.getScaleFieldForType(portal_type)
            defscale = kupu.getDefaultScaleForType(portal_type)
            classes = kupu.getClassesForType(portal_type)
            mediatype = kupu.getMediaForType(portal_type)
            res.append(dict(portal_type=portal_type,
                previewaction=previewaction,
                normalaction=normalaction,
                scalefield=scalefield,
                defscale=defscale,
                classes=classes,
                mediatype=mediatype,
            ))
        return res

    security.declarePrivate('_getExportTemplate')
    def _getExportTemplate(self):
        return PageTemplateFile('kupuExport.xml', _xmldir)

InitializeClass(KupuToolExportConfigurator)


class KupuToolImportConfigurator(ImportConfiguratorBase):

    def _getImportMapping(self):
        return {
            'kupu-settings':
                {
                    'config': {},
                    'library': { KEY: 'libraries' },
                    'defaultlibrary': { DEFAULT: ('',) },
                    'resource': { KEY: 'resources' },
                    'defaultresource': { DEFAULT: ('linkable',) },
                    'preview': { KEY: 'previews', DEFAULT: () },
                    'generatepreviews': {},
                    'globaltoolbar': { DEFAULT: ('',) },
                    'toolbar': {}
                },
            'config':
                {
                    'captioning': {CONVERTER: self._convertToBoolean, DEFAULT: False},
                    'userefbrowser': {CONVERTER: self._convertToBoolean, DEFAULT: False},
                    'linkbyuid': {CONVERTER: self._convertToBoolean, DEFAULT: False},
                    'filtersourceedit': {CONVERTER: self._convertToBoolean, DEFAULT: True},
                    'installbeforeunload': {CONVERTER: self._convertToBoolean, DEFAULT: False},
                    'table': {KEY: 'tableclasses', DEFAULT:() },
                    'style': {KEY: 'parastyles', DEFAULT:() },
                    'filter': {KEY: 'filters', DEFAULT:() },
                    'filterstyle': {KEY: 'filterstyles', DEFAULT:() },
                    'filterclass': {KEY: 'filterclasses', DEFAULT:() },
                },
            'table': { '#text': {KEY:None}, },
            'style': { '#text': {KEY:None}, },
            'filter':
                {
                    'attributes': {},
                    'tags': {},
                },
            'filterstyle': { '#text': {KEY:None}, },
            'filterclass': { '#text': {KEY:None}, },
            'library':
                {
                    'src': {},
                    'uri': {},
                    'id': {},
                    'icon': {},
                    'title': {},
                },
            'defaultlibrary': { '#text': { KEY:None }, },
            'resource':
                {
                    'mode': {},
                    'id': {},
                    'type': { KEY:'types' },
                },
            'defaultresource': { '#text': { KEY:None }, },
            'type':
                { '#text': { KEY: None },
                },
            'preview':
                {
                    'portaltype': { KEY: 'portal_type' },
                    'preview': { KEY:'expression', DEFAULT: ''},
                    'normal': { DEFAULT: ''},
                    'scalefield': { DEFAULT: 'image' },
                    'defscale': { DEFAULT: 'image_preview' },
                    'previewclass': { KEY: 'classes', DEFAULT: ()},
                    'mediatype': { DEFAULT: ''},
                },
            'previewclass': { '#text': {KEY:None}, },
            'generatepreviews': {},
            'globaltoolbar': { '#text': { KEY:None, DEFAULT: '' }, },
            'toolbar':
                {
                    'element': { KEY: 'elements' },
                },
            'element':
                {
                    'visible': {CONVERTER: self._convertToBoolean, DEFAULT: True},
                    'id': { '#text': None },
                    'expression':  { KEY: 'override', DEFAULT: '' },
                },
            }

InitializeClass(KupuToolImportConfigurator)
