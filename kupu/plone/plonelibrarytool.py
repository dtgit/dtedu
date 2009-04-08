# -*- coding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Plone Kupu library tool

This module contains the Plone specific version of the Kupu library
tool.

$Id: plonelibrarytool.py 51120 2008-01-30 10:18:06Z duncan $
"""
import os
from ZODB.PersistentList import PersistentList
from ZODB.PersistentMapping import PersistentMapping
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
import Globals
from Globals import InitializeClass

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import UniqueObject
from Products.PythonScripts.standard import Object

from Products.kupu.plone.librarytool import KupuLibraryTool
from Products.kupu.plone import permissions, scanner, plonedrawers, util, helpers
from Products.CMFCore.utils import getToolByName
from Products.kupu import kupu_globals
from Products.kupu.config import TOOLNAME, TOOLTITLE
from StringIO import StringIO
from urllib import quote_plus, unquote_plus
import html2captioned
try:
    from plone.app.controlpanel import filter
    HAVE_PLONE_FILTERING = True
except:
    HAVE_PLONE_FILTERING = False

# Zope 3 interfaces, but on older zopes we'll just skip this bit.
try:
    from zope.interface import implements
except ImportError:
    def implements(*args): pass

from z3interfaces import IPloneKupuLibraryTool

_default_libraries = (
    dict(id="root",
         title="string:Home",
         uri="string:${globals_view/navigationRootUrl|portal_url}",
         src="string:${globals_view/navigationRootUrl|portal_url}/kupucollection.xml",
         icon="string:${globals_view/navigationRootUrl|portal_url}/misc_/CMFPlone/plone_icon"),
    dict(id="current",
         title="string:Current folder",
         uri="string:${folder_url}",
         src="string:${folder_url}/kupucollection.xml",
         icon="string:${folder/getIcon}"),
    dict(id="myitems",
         title="string:My recent items",
         uri="string:${portal_url}/kupumyitems.xml",
         src="string:${portal_url}/kupumyitems.xml",
         icon="string:${portal_url}/kupuimages/kupusearch_icon.gif"),
    dict(id="recentitems",
         title="string:Recent items",
         uri="string:${portal_url}/kupurecentitems.xml",
         src="string:${portal_url}/kupurecentitems.xml",
         icon="string:${portal_url}/kupuimages/kupusearch_icon.gif")
    )

_default_resource_types = {
    'collection': ('Plone Site', 'Folder', 'Large Plone Folder'),
    'mediaobject': ('Image',),
    'linkable': ('Document', 'Image', 'File', 'News Item', 'Event', 'Folder', 'Large Plone Folder'),
    'containsanchors': ('Document', 'News Item', 'Event'),
    }

# Tidy up html by exlcluding lots of things.
_excluded_html = [
  (('center', 'tt', 'big', 'small', 'basefont', 'font'), ()),
  ((), ('lang','valign','halign','border','frame','rules','cellspacing','cellpadding','bgcolor')),
  (('table','th','td'),('width','height')),
]

# Default should list all styles used by Kupu
_style_whitelist = ['text-align', 'list-style-type', 'float']

_default_paragraph_styles = (
    "Heading|h2",
    "Subheading|h3",
    "Literal|pre",
    "Discreet|p|discreet",
    "Pull-quote|div|pullquote",
    "Call-out|p|callout",
    "Highlight|span|visualHighlight",
    "Odd row|tr|odd",
    "Even row|tr|even",
    "Heading cell|th|",
)

class PloneKupuLibraryTool(UniqueObject, SimpleItem, KupuLibraryTool,
    plonedrawers.PloneDrawers):
    """Plone specific version of the kupu library tool"""

    id = TOOLNAME
    meta_type = "Kupu Library Tool"
    title = TOOLTITLE
    security = ClassSecurityInfo()
    implements(IPloneKupuLibraryTool)

    # protect methods provided by super class KupuLibraryTool
    security.declareProtected(permissions.QueryLibraries, "getLibraries",
                              "getPortalTypesForResourceType")
    security.declareProtected(permissions.ManageLibraries, "addLibrary",
                              "deleteLibraries", "updateLibraries",
                              "moveUp", "moveDown")
    security.declareProtected(permissions.ManageLibraries, "addResourceType",
                              "updateResourceTypes", "deleteResourceTypes")

    def __init__(self):
        self._libraries = PersistentList()
        self._res_types = PersistentMapping()
        self.linkbyuid = False

    def manage_afterAdd(self, item, container):
        # We load default values here, so __init__ can still be used
        # in unit tests. Plus, it only makes sense to load these if
        # we're being added to a Plone site anyway
        if not len(self._libraries):
            for lib in _default_libraries:
                self.addLibrary(**lib)
            self._res_types.update(_default_resource_types)

    security.declareProtected('View', "getLinkbyuid")
    def getLinkbyuid(self):
        """Returns 'is linking by UID enabled'?"""
        try:
            return bool(self.linkbyuid)
        except AttributeError:
            return False

    security.declareProtected('View', "getRefBrowser")
    def getRefBrowser(self):
        """Returns True if kupu_references is in all skin layers"""
        return util.layer_installed(self, 'kupu_references')

    security.declareProtected(permissions.ManageLibraries, 'ensureReferencesLayer')
    def ensureReferencesLayer(self, add=False):
        """Called from the link tab code: we must have the
        kupu_references directory view at least present for
        the link tab to work."""
        out = StringIO()
        util.register_layer(self, 'plone/kupu_references', 'kupu_references', out, add)

    security.declareProtected('View', "getCaptioning")
    def getCaptioning(self):
        """Returns True if captioning is enabled"""
        try:
            return bool(self.captioning)
        except AttributeError:
            return False

    security.declareProtected('View', "getTableClassnames")
    def getTableClassnames(self):
        """Return a list of classnames supported in tables"""
        try:
            return self.table_classnames
        except AttributeError:
            return ('plain', 'listing', 'vertical listing', 'listing nosort|unsorted listing')

    security.declareProtected('View', "getParagraphStyles")
    def getParagraphStyles(self):
        """Return a list of classnames supported by paragraphs"""
        try:
            return self.paragraph_styles
        except AttributeError:
            return _default_paragraph_styles

    security.declareProtected('View', "getStyleList")
    def getStyleList(self, field=None):
        """Return the styles for a field."""
        gstyles = self.getParagraphStyles()
        if field:
            widget = field.widget
            redefine = getattr(widget, 'redefine_parastyles', False)
            lstyles = getattr(widget, 'parastyles', ())
        else:
            redefine = False
            lstyles = []

        result = []
        __traceback_info__ = (gstyles, lstyles)
        if redefine:
            styles = lstyles
        else:
            styles = list(gstyles) + list(lstyles)
            
        for style in styles:
            parts = style.split('|',1)+['','']
            value = parts[1]
            content = parts[0]
            result.append({'value':value, 'content':content})

        return result

    security.declareProtected('View', "filterToolbar")
    def filterToolbar(self, context, field=None):
        return helpers.ButtonFilter(self, context, field)

    security.declareProtected('View', "getFilterOptions")
    def getFilterOptions(self, field=None):
        filters = helpers.FILTERS
        config = self._getToolbarFilterOptions()
        res = []
        for (id, title, default, klass) in filters:
            cfg = config.get(id, {})
            visible = cfg.get('visible', default)
            expr = cfg.get('override', None)
            if expr is not None:
                expr = expr.text
            res.append(dict(id=id, title=title, visible=visible, override=expr, classname=klass))
        return res

    security.declareProtected(permissions.ManageLibraries, "set_toolbar_filters")
    def set_toolbar_filters(self, filters, globalfilter, REQUEST=None):
        """Set the toolbar filtering
        filter is a list of records with: id, checked, expression"""
        DEFAULTS = helpers.FILTERDICT
        def nonstandard(f):
            expr = f['override']
            id = f['id']
            visible = bool(f.get('visible', False))
            return expr != '' or visible != DEFAULTS.get(id, False)
            
        cleaned = [ f for f in filters if nonstandard(f) ]
        self._setToolbarFilters(cleaned, globalfilter)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_toolbar')

    security.declareProtected(permissions.ManageLibraries, "getGlobalButtonFilter")
    def getGlobalButtonFilter(self):
        gfilter = getattr(self, '_global_toolbar_filter', None)
        if gfilter is not None:
            return gfilter.text
        return ''

    security.declareProtected('View', "getHtmlExclusions")
    def getHtmlExclusions(self):
        try:
            excl = self.html_exclusions
        except AttributeError:
            excl = self.html_exclusions = _excluded_html

        res = []
        for (t,a) in excl:
            if t and t[0]=='':
                t = []
            if a and a[0]=='':
                a = []
            res.append((t,a))
        return res

    security.declareProtected('View', "getStyleWhitelist")
    def getStyleWhitelist(self):
        try:
            return self.style_whitelist
        except AttributeError:
            self.style_whitelist = _style_whitelist
            return self.style_whitelist

    security.declareProtected('View', "getClassBlacklist")
    def getClassBlacklist(self):
        return getattr(self, 'class_blacklist', [])

    security.declareProtected('View', "getDefaultResource")
    def getDefaultResource(self):
        return getattr(self, 'default_resource', 'linkable')

    security.declareProtected(permissions.ManageLibraries, "setDefaultResource")
    def setDefaultResource(self, resource_type):
        self.default_resource = resource_type

    security.declareProtected('View', "installBeforeUnload")
    def installBeforeUnload(self):
        return getattr(self, 'install_beforeunload', False)

    security.declareProtected('View', "getFiltersourceedit")
    def getFiltersourceedit(self):
        return getattr(self, 'filtersourceedit', True)

    security.declareProtected('View', "getAllowOriginalImageSize")
    def getAllowOriginalImageSize(self):
        return getattr(self, 'allowOriginalImageSize', False)

    security.declareProtected('View', 'isKupuEnabled')
    def isKupuEnabled(self, useragent='', allowAnonymous=False, REQUEST=None, context=None, fieldName=None):
        if not REQUEST:
            REQUEST = self.REQUEST
        def numerics(s):
            '''Convert a string into a tuple of all digit sequences
            '''
            seq = ['']
            for c in s:
                if c.isdigit():
                    seq[-1] = seq[-1] + c
                elif seq[-1]:
                    seq.append('')
            return tuple([ int(val) for val in seq if val])

        # First check whether the user actually wants kupu
        pm = getToolByName(self, 'portal_membership')
        if pm.isAnonymousUser() and not allowAnonymous:
            return False

        user = pm.getAuthenticatedMember()
        if not pm.isAnonymousUser():
            editor = user.getProperty('wysiwyg_editor')
            if editor and editor.lower() != 'kupu':
                return False

        # Then check whether the current content allows html
        if context is not None and fieldName and hasattr(context, 'getWrappedField'):
            field = context.getWrappedField(fieldName)
            if field:
                allowedTypes = getattr(field, 'allowable_content_types', None)
                if allowedTypes is not None and not 'text/html' in [t.lower() for t in allowedTypes]:
                    return False

        # Then check whether their browser supports it.
        if not useragent:
            useragent = REQUEST['HTTP_USER_AGENT']

        if 'BEOS' in useragent:
            return False

        def getver(s):
            """Extract a version number given the string which precedes it"""
            pos = useragent.find(s)
            if pos >= 0:
                tail = useragent[pos+len(s):].strip()
                verno = numerics(tail.split(' ')[0])
                return verno
            return None
            
        try:
            v = getver('Opera/')
            if not v:
                v = getver('Opera ')
            if v:
                return v >= (9,0)

            mozillaver = getver('Mozilla/')
            if mozillaver > (5,0):
                return True
            elif mozillaver == (5,0):
                verno = getver(' rv:')
                if verno:
                    return verno >= (1,3,1)
                verno = getver(' AppleWebKit/')
                if verno:
                    return verno >= (525,1)
                    verno = getver(' Safari/')
                    if verno:
                        return verno >= (522,12)

            verno = getver('MSIE')
            if verno:
                return verno >= (5,5)
        except:
            # In case some weird browser makes the test code blow up.
            pass
        return False

    security.declarePublic("getWysiwygmacros")
    def getWysiwygmacros(self):
        """Find the appropriate template to use for the kupu widget"""
        pm = getToolByName(self, 'portal_membership')
        user = pm.getAuthenticatedMember()
        editor = user.getProperty('wysiwyg_editor', '')
        if editor: editor = editor.lower()
        if editor=='fck editor':
            editor = 'editor_fck'

        portal = getToolByName(self, 'portal_url').getPortalObject()
        for path in ('%s_wysiwyg_support' % editor,
            '%s/wysiwyg_support' % editor,
            'portal_skins/plone_wysiwyg/wysiwyg_support'):
                template = portal.restrictedTraverse(path, None)
                if template:
                    break

        return template.macros

    security.declarePublic("forcekupu_url")
    def forcekupu_url(self, fieldName):
        args = {'kupu.convert':fieldName,
            'kupu.suppress':None,
            'portal_status_message':None
            }
        qs = self.query_string(args);
        return "%s?%s" % (self.REQUEST.URL0, qs)

    security.declarePublic("query_string")
    def query_string(self, replace={}, original=None):
        """ Updates 'original' dictionary by the values in the 'replace'
            dictionary and returns the result as url quoted query string.

            The 'original' dictionary defaults to 'REQUEST.form' if no
            parameter is passed to it. Keys in the 'replace' dictionary
            with a value of 'None' (or _.None in DTML) will be deleted
            from 'original' dictionary before being quoted.

            The original 'REQUEST.form' will remain unchanged.
        """
        # Based on code by Grégoire Weber
        if original is None:
            query = self.REQUEST.form.copy()
        else:
            query = original.copy()

        # delete key/value pairs if value is None
        for k,v in replace.items():
            if v is None:
                if query.has_key(k):
                    del query[k]
                del replace[k]

        # update dictionary
        query.update(replace)
        qs = '&'.join(["%s=%s" % (quote_plus(str(k)), quote_plus(str(v)))
            for k,v in query.items()])

        return qs

    security.declareProtected("View", "url_plus_query")
    def url_plus_query(self, url, query=None):
        """Adds query segment to an existing URL.
        Existing query parameters are may be overridden by query,
        otherwise they are preserved.
        """
        if query is None:
            query = {}
        parts = url.split('?', 1)
        oldargs = {}
        if len(parts) > 1:
            for arg in parts[1].split('&'):
                k,v = [unquote_plus(s) for s in arg.split('=',1)]
                oldargs[k] = v

        return "%s?%s" % (parts[0], self.query_string(query, oldargs))

    security.declareProtected('View', 'kupuUrl')
    def kupuUrl(self, url, query=None):
        """Generate a url which includes resource_type and instance"""
        request = self.REQUEST
        resource_type = request.get('resource_type', 'mediaobject')
        instance = request.get('instance', None)
        newquery = { 'instance':instance, 'resource_type':resource_type }
        if query is not None:
            newquery.update(query)
        return self.url_plus_query(url, newquery)
        
    security.declareProtected('View', "getCookedLibraries")
    def getCookedLibraries(self, context):
        """Return a list of libraries with our own parameters included.
        The library with id 'search' is excluded from this list."""
        libraries = [l for l in self.getLibraries(context) if not l['id'].startswith('_')]
        default_library = getattr(self, '_default_library', '')

        for l in libraries:
            l['src'] = self.kupuUrl(l['src'])
            l['selected'] = l['id']==default_library or None
        return libraries

    security.declareProtected('View', "getSingleLibrary")
    def getSingleLibrary(self, context, id):
        """Return the library with id=search or None"""
        libraries = [l for l in self.getLibraries(context) if l['id']==id]

        for l in libraries:
            l['src'] = self.kupuUrl(l['src'])
        if libraries:
            return libraries[0]
        return None

    # ZMI views
    manage_options = (SimpleItem.manage_options[1:] + (
         dict(label='Config', action='kupu_config'),
         dict(label='Libraries', action='zmi_libraries'),
         dict(label='Resource types', action='zmi_resource_types'),
         dict(label='Documentation', action='zmi_docs'),
         ))


    security.declarePublic('scanIds')
    def scanIds(self):
        """Finds the relevant source files and the doller/Id/dollar strings they contain"""
        return scanner.scanIds()

    security.declarePublic('scanKWS')
    def scanKWS(self):
        """Check that kupu_wysiwyg_support is up to date"""
        return scanner.scanKWS()

    security.declarePublic('docs')
    def docs(self):
        """Returns Kupu docs formatted as HTML"""
        docpath = os.path.join(Globals.package_home(kupu_globals), 'doc')
        f = open(os.path.join(docpath, 'PLONE2.txt'), 'r')
        _docs = f.read()
        return _docs

    security.declareProtected(permissions.ManageLibraries, "link_migration")
    def link_migration(self, action=None):
        """Do link checking or conversion, a little bit at a time"""
        if action is None:
            action = self.REQUEST.form.get('button', '')

        commit = self.REQUEST.form.get('commit', False)
        migrator = html2captioned.Migration(self)
        if action=='continue':
            migrator.restoreState()
            res = migrator.docontinue()
            return migrator.getInfo()
        elif action=='status':
            try:
                migrator.restoreState()
            except KeyError:
                return "state cleared"
            return migrator.status()
        elif action=='query':
            migrator.initFromRequest()
            return migrator.mkQuery()
        elif commit:
            migrator.initCommit()
            return migrator.getInfo()
        else:
            migrator.initFromRequest()
            return migrator.getInfo()

    security.declareProtected(permissions.ManageLibraries, "zmi_links")
    zmi_links = PageTemplateFile("zmi_links.pt", globals())
    zmi_links.title = 'kupu link maintenance'

    security.declareProtected(permissions.ManageLibraries, "zmi_toolbar")
    zmi_toolbar = PageTemplateFile("zmi_toolbar.pt", globals())
    zmi_toolbar.title = 'kupu toolbar customisation'

    security.declareProtected(permissions.ManageLibraries, "zmi_docs")
    zmi_docs = PageTemplateFile("zmi_docs.pt", globals())
    zmi_docs.title = 'kupu configuration documentation'

    security.declareProtected(permissions.ManageLibraries, "kupu_config")
    kupu_config = PageTemplateFile("kupu_config.pt", globals())
    kupu_config.title = 'kupu configuration'

    security.declareProtected(permissions.ManageLibraries, "zmi_libraries")
    zmi_libraries = PageTemplateFile("libraries.pt", globals())
    zmi_libraries.title = 'kupu configuration'

    security.declareProtected(permissions.ManageLibraries, "zmi_resource_types")
    zmi_resource_types = PageTemplateFile("resource_types.pt", globals())
    zmi_resource_types.title = 'kupu configuration'

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_get_libraries")
    def zmi_get_libraries(self):
        """Return the libraries sequence for the ZMI view"""
        #return ()
        def text(value):
            return getattr(value, 'text', value)
        return [dict([(key, text(value)) for key, value in lib.items()])
                for lib in self._libraries]

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_add_library")
    def zmi_add_library(self, id, title, uri, src, icon, REQUEST):
        """Add a library through the ZMI"""
        self.addLibrary(id, title, uri, src, icon)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_libraries')

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_update_libraries")
    def zmi_update_libraries(self, libraries, REQUEST):
        """Update libraries through the ZMI"""
        self.updateLibraries(libraries)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_libraries')

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_delete_libraries")
    def zmi_delete_libraries(self, indices, REQUEST):
        """Delete libraries through the ZMI"""
        self.deleteLibraries(indices)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_libraries')

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_move_up")
    def zmi_move_up(self, indices, REQUEST):
        """Move libraries up through the ZMI"""
        self.moveUp(indices)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_libraries')

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_move_down")
    def zmi_move_down(self, indices, REQUEST):
        """Move libraries down through the ZMI"""
        self.moveDown(indices)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_libraries')

    security.declarePublic("zmi_get_default_library")
    def zmi_get_default_library(self):
        """Return the default selected library for the ZMI view"""
        return getattr(self, '_default_library', '')

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_set_default_library")
    def zmi_set_default_library(self, defid=''):
        """Return the libraries sequence for the ZMI view"""
        self._default_library = defid

    security.declareProtected(permissions.ManageLibraries, "zmi_get_type_mapping")
    def zmi_get_type_mapping(self):
        """Return the type mapping for the ZMI view:
           Old version of code. Returns name,types pairs plus a dummy"""
        return [(t.name, t.types) for t in self.zmi_get_resourcetypes()] + [('',())]

    security.declareProtected(permissions.ManageLibraries, "export_resource_types")
    def export_resource_types(self):
        """Build a list of resource types formatted for export.
        'blacklist' type lists are inverted so the listed types are the ones we don't want.
        """
        types = self.get_resourcetypes()
        typetool = getToolByName(self, 'portal_types')
        portal_types = dict([ (t.id, 1) for t in typetool.listTypeInfo()])
        for t in types:
            if t.newtype:
                t.types = self.invertTypeList(t.types)
                t.mode = 'blacklist'
            else:
                t.mode = 'whitelist'
        return types

    security.declareProtected(permissions.ManageLibraries, "get_resourcetypes")
    def get_resourcetypes(self):
        """Return the type mapping, but without the ZMI dummy entry"""
        keys = self._res_types.keys()
        keys.sort()
        real = []
        for name in keys:
            value = self._res_types[name]
            wrapped = Object(name=name, types=tuple(value), newtype=self.getNewTypeHandler(name))
            real.append(wrapped)
        return real

    security.declareProtected(permissions.ManageLibraries, "zmi_get_resourcetypes")
    def zmi_get_resourcetypes(self):
        """Return the type mapping for the ZMI view"""
        real = self.get_resourcetypes()
        real.append(Object(name='', types=()))
        return real

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_update_resource_types")
    def zmi_update_resource_types(self, type_info=None, preview_action=None, default_resource=None, REQUEST=None):
        """Update resource types through the ZMI"""

        if type_info:
            self.updateResourceTypes(type_info)

        if preview_action:
            self.updatePreviewActions(preview_action)

        if default_resource is not None:
            self.default_resource = default_resource

        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_resource_types')

    security.declareProtected(permissions.ManageLibraries,
                              "zmi_delete_resource_types")
    def zmi_delete_resource_types(self, resource_types=None, preview_types=None, REQUEST=None):
        """Delete resource types through the ZMI"""
        if resource_types:
            self.deleteResourceTypes(resource_types)
        if preview_types:
            self.deletePreviewActions(preview_types)
        if (REQUEST):
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/zmi_resource_types')

    security.declareProtected(permissions.ManageLibraries, "getPreviewForType")
    def getPreviewForType(self, portal_type):
        action_map = getattr(self, '_preview_actions', {})
        expr = action_map.get(portal_type, {}).get('expression', '')
        return getattr(expr, 'text', expr)

    security.declareProtected(permissions.ManageLibraries, "getNormalViewForType")
    def getNormalViewForType(self, portal_type):
        action_map = getattr(self, '_preview_actions', {})
        expr = action_map.get(portal_type, {}).get('normal', '')
        return getattr(expr, 'text', expr)

    security.declareProtected(permissions.ManageLibraries, "getScaleFieldForType")
    def getScaleFieldForType(self, portal_type):
        action_map = getattr(self, '_preview_actions', {})
        value = action_map.get(portal_type, {}).get('scalefield', 'image')
        return value

    security.declareProtected(permissions.ManageLibraries, "getDefaultScaleForType")
    def getDefaultScaleForType(self, portal_type):
        action_map = getattr(self, '_preview_actions', {})
        value = action_map.get(portal_type, {}).get('defscale', 'image_preview')
        return value

    security.declareProtected(permissions.ManageLibraries, "getClassesForType")
    def getClassesForType(self, portal_type):
        action_map = getattr(self, '_preview_actions', {})
        return action_map.get(portal_type, {}).get('classes', ())

    security.declareProtected(permissions.ManageLibraries, "getMediaForType")
    def getMediaForType(self, portal_type):
        action_map = getattr(self, '_preview_actions', {})
        value = action_map.get(portal_type, {}).get('mediatype', 'image')
        return value

    security.declareProtected(permissions.ManageLibraries, "set_html_exclusions")
    def set_html_exclusions(self, exclusions):
        """Set the html_exclusions.
        Expects a list/tuple of 2-tuples [(tags,attrs),...]
        """
        excl = []
        for (tags,attrs) in exclusions:
            if len(tags)==1 and tags[0]=="":
                tags = []
            if len(attrs)==1 and attrs[0]=="":
                attrs = []
            excl.append((tags, attrs))
        self.html_exclusions = excl

    security.declareProtected("View", "get_stripped_tags")
    def get_stripped_tags(self):
        """Returns a list of tags to be stripped"""
        stripped = []
        for (tags, attrs) in self.getHtmlExclusions():
            if not attrs:
                stripped.extend(tags)
        return stripped

    security.declareProtected(permissions.ManageLibraries, "set_stripped_tags")
    def set_stripped_tags(self, stripped):
        """Sets a list of tags to be stripped"""
        exclusions = [(tags, attrs) for (tags, attrs) in self.getHtmlExclusions() if attrs]
        exclusions.append((tuple(stripped), ()))
        self.set_html_exclusions(exclusions)

    security.declareProtected('View', "get_stripped_attributes")
    def get_stripped_attributes(self):
        """Returns a list of attributes to be stripped"""
        stripped = []
        for (tags, attrs) in self.getHtmlExclusions():
            if not tags:
                stripped.extend(attrs)
        return stripped
        
    security.declareProtected(permissions.ManageLibraries, "set_stripped_attributes")
    def set_stripped_attributes(self, stripped):
        """Sets a list of attributes to be stripped"""
        exclusions = [(tags, attrs) for (tags, attrs) in self.html_exclusions if tags]
        exclusions.append(((), tuple(stripped)))
        self.set_html_exclusions(exclusions)

    security.declareProtected('View', "get_stripped_combinations")
    def get_stripped_combinations(self):
        """Returns a list of tag/attribute combinations to be stripped"""
        stripped = [(tags, attrs) for (tags, attrs) in self.getHtmlExclusions() if tags and attrs]
        return stripped

    security.declareProtected(permissions.ManageLibraries, "set_stripped_combinations")
    def set_stripped_combinations(self, stripped):
        """Sets a list of tag/attribute pairs to be stripped"""
        exclusions = [(tags, attrs) for (tags, attrs) in self.getHtmlExclusions() if not (tags and attrs)]
        self.set_html_exclusions(stripped + exclusions)


    security.declareProtected('View', "have_plone_filtering")
    def have_plone_filtering(self):
        return HAVE_PLONE_FILTERING

    security.declareProtected(permissions.ManageLibraries,
                              "configure_kupu")
    def configure_kupu(self,
        linkbyuid=None,
        table_classnames=None,
        html_exclusions=None,
        style_whitelist=None,
        class_blacklist=None,
        installBeforeUnload=None, parastyles=None, refbrowser=None,
        captioning=None,
        filterSourceEdit=None,
        allowOriginalImageSize=None,
        REQUEST=None):
        """Delete resource types through the ZMI"""
        if linkbyuid is not None:
            self.linkbyuid = bool(linkbyuid)
        if table_classnames is not None:
            self.table_classnames = [t for t in table_classnames if t]
        if installBeforeUnload is not None:
            self.install_beforeunload = bool(installBeforeUnload)
        if filterSourceEdit is not None:
            self.filtersourceedit = bool(filterSourceEdit)
        if allowOriginalImageSize is not None:
            self.allowOriginalImageSize = bool(allowOriginalImageSize)

        if parastyles is not None:
            self.paragraph_styles = [ line.strip() for line in parastyles if line.strip() ]

        if html_exclusions is not None:
            newex = html_exclusions[-1]
            html_exclusions = html_exclusions[:-1]
            
            html_exclusions = [ (tuple(h.get('tags', ())), tuple(h.get('attributes', ())))
                for h in html_exclusions if h.get('keep')]

            tags = newex.get('tags', '').replace(',',' ').split()
            attr = newex.get('attributes', '').replace(',',' ').split()
            if tags or attr:
                html_exclusions.append((tuple(tags), tuple(attr)))
            self.set_html_exclusions(html_exclusions)

        if style_whitelist is not None:
            self.style_whitelist = list(style_whitelist)
        if class_blacklist is not None:
            self.class_blacklist = list(class_blacklist)

        if refbrowser is not None:
            out = StringIO()
            if refbrowser:
                self.ensureReferencesLayer(True);
            else:
                util.unregister_layers(self, ['kupu_references'], out)
            # Force compressed javascript to be recomputed.
            try:
                self.portal_javascripts.cookResources()
            except AttributeError:
                pass

        if captioning is not None:
            self.captioning = bool(captioning)

        if self.linkbyuid or self.captioning:
            util.install_transform(self)
        else:
            util.remove_transform(self)

        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/kupu_config')
        
InitializeClass(PloneKupuLibraryTool)
