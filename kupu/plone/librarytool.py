##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Kupu library tool

This module contains Kupu's library tool to support drawers.

$Id: librarytool.py 45155 2007-07-17 09:38:27Z duncan $
"""
import Acquisition
from Acquisition import aq_parent, aq_inner, aq_base
from Products.CMFCore.Expression import Expression, createExprContext
from Products.PageTemplates.Expressions import getEngine, SecureModuleImporter
from Products.kupu.plone.interfaces import IKupuLibraryTool
from Products.CMFCore.utils import getToolByName

class KupuError(Exception): pass
NEWTYPE_IGNORE, NEWTYPE_ADD = 0, 1

class Resource:
    """Class to hold resources"""
    
class KupuLibraryTool(Acquisition.Implicit):
    """A tool to aid Kupu libraries"""

    __implements__ = IKupuLibraryTool

    def __init__(self):
        self._libraries = []
        self._res_types = {}

    def _getExpressionContext(self, object):
        portal = aq_parent(aq_inner(self))
        if object is None or not hasattr(object, 'aq_base'):
            folder = portal
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    folder = aq_parent(aq_inner(folder))
        ec = createExprContext(folder, portal, object)
        return ec

    def addLibrary(self, id, title, uri, src, icon):
        """See ILibraryManager"""
        lib = dict(id=id, title=title, uri=uri, src=src, icon=icon)
        for key, value in lib.items():
            if key=='id':
                lib[key] = value
            else:
                if not(value.startswith('string:') or value.startswith('python:')):
                    value = 'string:' + value
                lib[key] = Expression(value)
        self._libraries.append(lib)

    def getLibraries(self, context):
        """See ILibraryManager"""
        expr_context = self._getExpressionContext(context)
        libraries = []
        for library in self._libraries:
            lib = {}
            for key in library.keys():
                if isinstance(library[key], str):
                    lib[key] = library[key]
                else:
                    # Automatic migration from old version.
                    if key=='id':
                        lib[key] = library[key] = library[key].text
                    else:
                        lib[key] = library[key](expr_context)
            libraries.append(lib)
        return tuple(libraries)

    def deleteLibraries(self, indices):
        """See ILibraryManager"""
        indices.sort()
        indices.reverse()
        for index in indices:
            del self._libraries[index]

    def updateLibraries(self, libraries):
        """See ILibraryManager"""
        for index, lib in enumerate(self._libraries):
            dic = libraries[index]
            for key in lib.keys():
                if dic.has_key(key):
                    value = dic[key]
                    if key=='id':
                        lib[key] = value
                    else:
                        if not(value.startswith('string:') or
                               value.startswith('python:')):
                            value = 'string:' + value
                        lib[key] = Expression(value)
            self._libraries[index] = lib

    def moveUp(self, indices):
        """See ILibraryManager"""
        indices.sort()
        libraries = self._libraries[:]
        for index in indices:
            new_index = index - 1
            libraries[index], libraries[new_index] = \
                              libraries[new_index], libraries[index]
        self._libraries = libraries

    def moveDown(self, indices):
        """See ILibraryManager"""
        indices.sort()
        indices.reverse()
        libraries = self._libraries[:]
        for index in indices:
            new_index = index + 1
            if new_index >= len(libraries):
                new_index = 0
                #new_index = ((index + 1) % len(libraries)) - 1
            libraries[index], libraries[new_index] = \
                              libraries[new_index], libraries[index]
        self._libraries = libraries

    def getNewTypeHandler(self, resource_type):
        """Should unknown portal types be added to the list or ignored"""
        _res_newtype = getattr(self, '_res_newtype', None)
        if _res_newtype is None:
            self._res_newtype = _res_newtype = {}
            for k in self._res_types:
                if k in ('linkable', 'containsanchors', 'composable'):
                    _res_newtype[k] = NEWTYPE_ADD
                else:
                    _res_newtype[k] = NEWTYPE_IGNORE
            self._res_newtype = _res_newtype

        return _res_newtype.get(resource_type, NEWTYPE_IGNORE)

    def setNewTypeHandler(self, resource_type, mode):
        """Update how unknown types are handled."""
        if self.getNewTypeHandler(resource_type) != mode:
            self._res_newtype[resource_type] = mode
            self._res_newtype = self._res_newtype # Flag ourselves as modified.

    def checkNewResourceTypes(self, resource_type=None):
        # Check for new types added. It would be nice if this
        # was called automatically but not every time we query a
        # resource.
        if resource_type != None:
            handle_new = self.getNewTypeHandler(resource_type)
            if handle_new == NEWTYPE_IGNORE:
                return
                
        typetool = getToolByName(self, 'portal_types')
        new_portal_types = dict([ (t.id, 1) for t in typetool.listTypeInfo()])
        if getattr(self, '_last_known_types', None) is None:
            # Migrate from old version
            self._last_known_types = new_portal_types
        else:
            for t in self._last_known_types:
                if t in new_portal_types:
                    del new_portal_types[t]
            if new_portal_types:
                self._addNewTypesToResources()

    def _addNewTypesToResources(self):
        """This method is called when the list of types in the system has changed.
        It updates all current resource types to include or exclude new types as
        appropriate.
        """
        typetool = getToolByName(self, 'portal_types')
        alltypes = typetool.listTypeInfo()
        lastknown = self._last_known_types
        newtypes = dict.fromkeys([ t.id for t in alltypes if t.id not in lastknown])

        for resource_type in self._res_types.keys():
            handle_new = self.getNewTypeHandler(resource_type)
            if handle_new==NEWTYPE_ADD:
                types = dict.fromkeys(self._res_types[resource_type])
                types.update(newtypes)
                self._res_types[resource_type] = types.keys()
        self._res_types = self._res_types
        
    def getPortalTypesForResourceType(self, resource_type):
        """See IResourceTypeMapper"""
        self.checkNewResourceTypes()
        types = self._res_types[resource_type]
        return types[:]

    def queryPortalTypesForResourceType(self, resource_type, default=None):
        """See IResourceTypeMapper"""
        if not self._res_types.has_key(resource_type):
            return default
        return self.getPortalTypesForResourceType(resource_type)

    def _validate_portal_types(self, resource_type, portal_types):
        typetool = getToolByName(self, 'portal_types')
        all_portal_types = dict([ (t.id, 1) for t in typetool.listTypeInfo()])

        portal_types = [ptype.strip() for ptype in portal_types if ptype]
        for p in portal_types:
            if p not in all_portal_types:
                raise KupuError, "Resource type: %s, invalid type: %s" % (resource_type, p)
        return portal_types

    def invertTypeList(self, types):
        """Convert a list of portal_types to a list of all the types not in the list"""
        typetool = getToolByName(self, 'portal_types')
        portal_types = dict([ (t.id, 1) for t in typetool.listTypeInfo()])
        res = [ name for name in portal_types if name not in types ]
        res.sort()
        return res

    def addResourceType(self, resource_type, portal_types, mode='whitelist'):
        """See IResourceTypeMapper"""
        newtype = NEWTYPE_IGNORE
        if mode != 'whitelist':
            portal_types = self.invertTypeList(portal_types)
            newtype = NEWTYPE_ADD
        portal_types = self._validate_portal_types(resource_type, portal_types)
        self._res_types[resource_type] = tuple(portal_types)
        self.setNewTypeHandler(resource_type, newtype)

    def updateResourceTypes(self, type_info):
        """See IResourceTypeMapper"""
        type_map = self._res_types
        
        for type in type_info:
            resource_type = type['resource_type']
            if not resource_type:
                continue
            portal_types = self._validate_portal_types(resource_type, type.get('portal_types', ()))
            old_type = type.get('old_type', None)
            if old_type:
                del type_map[old_type]
            type_map[resource_type] = tuple(portal_types)
            nt = type.get('newtypes', None)
            if nt is not None:
                self.setNewTypeHandler(resource_type, nt)

    def updatePreviewActions(self, preview_actions):
        """Now a misnomer: actually updates preview, normal, and scaling data"""
        action_map = {}

        for a in preview_actions:
            portal_type = a.get('portal_type', '')
            preview = a.get('expression', '')
            normal = a.get('normal', None)
            if normal:
                normal = Expression(normal)
            scalefield = a.get('scalefield', 'image')
            defscale = a.get('defscale', 'image_preview')
            classes = a.get('classes', '')
            if isinstance(classes, basestring):
                classes = classes.split('\n')
            classes = tuple(classes)
            mediatype = a.get('mediatype', 'image')
            if not portal_type:
                continue
            action_map[portal_type] = {
                'expression': Expression(preview),
                'normal': normal,
                'scalefield': scalefield,
                'defscale': defscale,
                'classes': classes,
                'mediatype': mediatype,
            }
        self._preview_actions = action_map

    def deleteResourceTypes(self, resource_types):
        """See IResourceTypeMapper"""
        existing = self._res_types
        for type in resource_types:
            if existing.has_key(type):
                del existing[type]

    def deletePreviewActions(self, preview_types):
        """See IResourceTypeMapper"""
        action_map = getattr(self, '_preview_actions', {})
        for type in preview_types:
            del action_map[type]
        self._preview_actions = action_map

    def getPreviewUrl(self, portal_type, url):
        action_map = getattr(self, '_preview_actions', {})
        if portal_type in action_map:
            expr = action_map[portal_type]['expression']
            if expr:
                data = {
                    'object_url':   url,
                    'portal_type':  portal_type,
                    'modules':      SecureModuleImporter,
                }
                context = getEngine().getContext(data)
                return expr(context)
        return None

    def getNormalUrl(self, portal_type, url):
        action_map = getattr(self, '_preview_actions', {})
        if portal_type in action_map:
            expr = action_map[portal_type].get('normal', None)
            if expr:
                data = {
                    'object_url':   url,
                    'portal_type':  portal_type,
                    'modules':      SecureModuleImporter,
                }
                context = getEngine().getContext(data)
                return expr(context)
        return url

    def _setToolbarFilters(self, filters, globalfilter):
        """Set the toolbar filtering
        filter is a list of records with: id, visible, override"""
        clean = {}
        for f in filters:
            id = f['id']
            visible = bool(f.get('visible', False))
            expr = f.get('override', None)

            if not id:
                continue

            if expr:
                expr = Expression(expr)
            else:
                expr = None
            clean[id] = dict(id=id, visible=visible, override=expr)

        self._toolbar_filters = clean
        if globalfilter:
            self._global_toolbar_filter = Expression(globalfilter)
        else:
            self._global_toolbar_filter = None

    def getToolbarFilters(self, context, field=None):
        expr_context = self._getExpressionContext(context)
        expr_context.setGlobal('field', field)
        filters = getattr(self, '_toolbar_filters', {})
        gfilter = getattr(self, '_global_toolbar_filter', None)
        if gfilter:
            gvisible = gfilter(expr_context)
        else:
            gvisible = None

        visible = {}
        for k in filters:
            f = filters[k]
            override = f.get('override', None)
            if override:
                visible[k] = bool(override(expr_context))
            else:
                visible[k] = f['visible']
        return visible, gvisible

    def _getToolbarFilterOptions(self):
        return getattr(self, '_toolbar_filters', {})

    def spellcheck(self, REQUEST):
        from Products.kupu.python.spellcheck import SpellChecker, format_result
        data = REQUEST["text"]
        c = SpellChecker()
        result = c.check(data)
        if result == None:
            result = ""
        else:
            result = format_result(result)
        REQUEST.RESPONSE.setHeader("Content-Type","text/xml, charset=utf-8")
        REQUEST.RESPONSE.setHeader("Content-Length",str(len(result)))
        return result
