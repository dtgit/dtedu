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

This module defines a mixin class for the kupu tool which contains
support code for drawers. Much of this code was formerly in separate
Python scripts, but has been moved here to make it easier to maintain.

"""
import re, string
from thread import get_ident
from AccessControl import Unauthorized, ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from Products.Archetypes.public import *
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.Archetypes.utils import shasattr
from Products.PythonScripts.standard import html_quote, newline_to_br
from Products.kupu.plone import util
from Products.kupu.plone.librarytool import KupuError
from Products.CMFCore.utils import getToolByName
try:
    from Products.CMFPlone.utils import getSiteEncoding
except ImportError:
    def getSiteEncoding(context):
        tool = getToolByName(context, 'plone_utils')
        return tool.getSiteEncoding()
    
import html2captioned

try:
    from PIL import Image
except ImportError:
    HAS_PIL = False
else:
    HAS_PIL = True

UIDURL = re.compile(".*\\bresolveuid/([^/?#]+)")
NOCC = nocc = string.maketrans(''.join([chr(c) for c in range(32) if c not in (9,10,13)]), "?"*29)
uNOCC = dict([(c,ord('?')) for c in range(32) if c not in (9,10,13)])
def filterControlChars(s):
    """convert characters which are illegal in xml to '?'"""
    if isinstance(s, unicode):
        return s.translate(uNOCC)
    else:
        return s.translate(NOCC)

# mapping (thread-id, portal-physicalPath, portal_type) ->
# imagefield-getAvailableSizes (as tuple sorted by dimension) (width, height, key)
IMAGE_SIZES_CACHE = {}

class ResourceType:
    '''Resource types are wrapped into a class so we can easily
    access attributes which may, or may not be present.
    '''
    def __init__(self, tool, name):
        self.name = name
        self._tool = tool
        parts = name.split('.', 1)
        self.subObject = None

        if len(parts)==1:
            self._portal_types = tool.queryPortalTypesForResourceType(name, ())
            self._field = self._widget = None
        else:
            # Must be portal_type.fieldname
            typename, fieldname = parts
            # Topic criteria have typename and fieldname embedded in
            # the criteria name.
            if fieldname.startswith('crit__'):
                self.subObject = '_'.join(fieldname.split('_')[:-1])
                typename, fieldname = fieldname.split('_')[-2:]

            __traceback_info__ = (parts, typename, fieldname)
            archetype_tool = getToolByName(tool, 'archetype_tool', None)
            types = archetype_tool.listRegisteredTypes()
            typeinfo = [t for t in types if t['portal_type']==typename]

            if len(typeinfo)==0:
                raise KupuError("Unrecognised portal type for resource %s" % name)

            schema = typeinfo[0]['schema']
            self.klass = typeinfo[0]['klass']
            try:
                self._field = schema[fieldname]
            except KeyError:
                raise KupuError("Unrecognised fieldname for resource %s" % name)
                
            self._widget = self._field.widget

    def __repr__(self):
        return "<ResourceType %s %s %s %s %s" % (
            self.name,
            self.portal_types, self.getQuery(), self.allow_browse, self.startup_directory
            )

    def get_portal_types(self):
        if not hasattr(self, '_portal_types'):
            field = self._field
            allowed_types = getattr(field, 'allowed_types', ())

            if allowed_types == ():
                dr = self._tool.getDefaultResource()
                allowed_types = self._tool.getResourceType(dr).portal_types

            allow_method = getattr(field, 'allowed_types_method', None)
            if allow_method is not None:
                instance = self._instanceFromRequest()
                if instance:
                    meth = getattr(instance, allow_method)
                    allowed_types = meth()
            self._portal_types = allowed_types

        return self._portal_types
    portal_types = property(get_portal_types)

    def getQuery(self):
        query = {'portal_type': self.portal_types }
        
        if self._field is not None:
            field = self._field
            widget = field.widget
            base_query = getattr(widget, 'base_query', None)
            if base_query and isinstance(base_query, basestring):
                # We need the actual object containing the field to be
                # able to call a dynamic base_query
                instance = self._instanceFromRequest()
                if instance:
                    base_query = getattr(instance, base_query, None)
                    if base_query:
                       base_query = base_query()
                       
            if base_query:
                query.update(base_query)

        return query

    def _instanceFromRequest(self):
        """Get instance object from UID in request.
        Throws an error if there isn't a UID.
        """
        if not hasattr(self, '_instance'):
            # XXX TODO: this needs to handle the case where the object is
            # being created through portal_factory and hasn't yet been
            # saved. The UID won't be in the catalog so we need to create
            # a dummy object instead.
            tool = self._tool
            UID = tool.REQUEST.get('instance', None)
            if UID is None:
                return None
            reference_tool = getToolByName(tool, 'reference_catalog')
            self._instance = reference_tool.lookupObject(UID)
        if self.subObject:
            return self._instance[self.subObject]

        return self._instance

    def _allow_browse(self):
        return getattr(self._widget, 'allow_browse', True)
    allow_browse = property(_allow_browse)

    def _startup_directory(self):
        return getattr(self._widget, 'startup_directory', '')
    startup_directory = property(_startup_directory)

class InfoAdaptor:
    """Convert either an object or a brain into an information dictionary."""
    def __init__(self, tool, resource_type, portal):
        self.url_tool = getToolByName(portal, 'portal_url')
        self.uid_catalog = getToolByName(portal, 'uid_catalog', None)
        self.portal_interface = getToolByName(portal, 'portal_interface')
        self.workflow_tool = getToolByName(portal, 'portal_workflow')
        self.workflow_states = self.wfTitles()
        self.linkbyuid = tool.getLinkbyuid()
        self.coll_types = tool.getResourceType('collection').portal_types
        self.anchor_types =  tool.getResourceType('containsanchors').portal_types
        self.portal_base = self.url_tool.getPortalPath()
        self.prefix_length = len(self.portal_base)+1
        self.resource_type = resource_type
        self.ttool = getToolByName(portal, 'portal_types')
        
        instance = tool.REQUEST.get('instance', '')
        if instance:
            instance = 'instance=%s&' % tool.REQUEST.instance

        self.srctail = 'kupucollection.xml?'+instance+'resource_type=' + resource_type.name
        self.showimagesize = resource_type.name=='mediaobject'

        # The redirecting url must be absolute otherwise it won't work for
        # preview when the page is using portal_factory
        # The absolute to relative conversion when the document is saved
        # should strip the url right back down to resolveuid/whatever.
        self.base = self.url_tool()
        self.security = getSecurityManager()
        self.tool = tool

    def wfTitles(self):
        wt = self.workflow_tool
        try:
            states = wt.listWFStatesByTitle()
        except AttributeError:
            # Older Plone versions
            states = {}
            for wf in wt.objectValues():
                state_folder = getattr(wf, 'states', None)
                if state_folder is not None:
                    for s in state_folder.objectValues():
                        title, id = s.title, s.getId()
                        if title:
                            states[id] = title
            return states

        return dict([(id,title) for (title,id) in states])

    def icon(self, portal_type):
        type = self.ttool.getTypeInfo(portal_type)
        if type is None:
            return None
        return "%s/%s" % (self.base, type.getIcon())

    def media(self, portal_type):
        """Get the media type to be included in the xml.
        Since 'image' is the default we can omit it."""
        media = self.tool.getMediaForType(portal_type)
        if media=='image':
            return None
        return media

    def classes(self, portal_type):
        stored = self.tool.getClassesForType(portal_type)
        classes = []
        for c in stored:
            c = c.strip()
            if not c:
                continue
            if '|' in c:
                title, classname = c.split('|', 1)
                classes.append({'title': title, 'classname': classname})
            else:
                classes.append({'title': c, 'classname': c})
        return classes

    def sizes(self, obj):
        """Returns size, width, height"""
        if not self.showimagesize:
            return None, None, None
        try:
            if not callable(obj.getId):
                obj = obj.getObject() # Must be a brain
            size = self.tool.getObjSize(obj)
        except:
            size = None

        width = getattr(obj, 'width', None)
        height = getattr(obj, 'height', None)
        if callable(width): width = width()
        if callable(height): height = height()
        return size, width, height

    def get_image_sizes(self, obj, portal_type, url):
        cache_key = (get_ident(), self.portal_base, portal_type)
        if not IMAGE_SIZES_CACHE.has_key(cache_key):
            IMAGE_SIZES_CACHE[cache_key] = {}
            imagefield = self.tool.getScaleFieldForType(portal_type)
            # if getId is not callable, we assume that we have a brain and
            # need to get the object
            if not callable(obj.getId):
                if getattr(obj, 'getObject', None) is None:
                    return
                try:
                    obj = obj.getObject()
                except:
                    return 
                
            if getattr(obj, 'getField', None) is None:
                return
            image_field = obj.getWrappedField(imagefield)
            if image_field is None:
                return
            if getattr(image_field, 'getAvailableSizes', None) is None:
                return
            image_sizes = image_field.getAvailableSizes(obj)
            sizes = [(v[0], v[1], k, '%s_%s' % (imagefield,k)) for k,v in image_sizes.items()]
            sizes.sort()
            sizes.reverse()
            IMAGE_SIZES_CACHE[cache_key] = sizes
        else:
            sizes = IMAGE_SIZES_CACHE[cache_key]
        results = []
        for width, height, key, action in sizes:
            results.append({'label':"%s (%s, %s)" % (key.capitalize(), width, height),
                            'uri':"%s/%s" % (url, action),
                            'action': action},)
        return results
    
    def getState(self, review_state):
        if review_state:
            className = 'state-'+review_state
            review_state = self.workflow_states.get(review_state, review_state)
        else:
            className = None
        return review_state, className

    def info_object(self, obj, allowLink=True):
        '''Get information from a content object'''

        # Parent folder might not be accessible if we came here from a
        # search.
        if not self.security.checkPermission('View', obj):
            return None

        __traceback_info__ = (obj, allowLink)
        id = None
        UID = None
        try:
            if self.portal_interface.objectImplements(obj,
                'Products.Archetypes.interfaces.referenceable.IReferenceable'):
                UID = getattr(obj.aq_explicit, 'UID', None)
                if UID:
                    UID = UID()
                    id = UID

            if not id:
                id = obj.absolute_url(relative=1)

            portal_type = getattr(obj, 'portal_type','')
            collection = portal_type in self.coll_types
            tool = self.tool
            url = obj.absolute_url()
            preview = tool.getPreviewUrl(portal_type, url)

            if collection and self.resource_type.allow_browse:
                src = obj.absolute_url()
                if not src.endswith('/'): src += '/'
                src += self.srctail
            else:
                src = None

            if UID and self.linkbyuid:
                url = self.base+'/resolveuid/%s' % UID

            if self.showimagesize:
                normal = tool.getNormalUrl(portal_type, url)
            else:
                normal = url

            sizes = self.get_image_sizes(obj, portal_type, url)
            defscale = self.tool.getDefaultScaleForType(portal_type)

            media = self.media(portal_type)
            classes = self.classes(portal_type)

            icon = self.icon(portal_type)
            size, width, height = self.sizes(obj)

            title = filterControlChars(obj.Title() or obj.getId())
            description = newline_to_br(html_quote(obj.Description()))

            linkable = None
            if allowLink:
                linkable = True
                collection = False

            anchor = portal_type in self.anchor_types
            review_state, className = self.getState(self.workflow_tool.getInfoFor(obj, 'review_state', None))

            return {
                'id': id,
                'url': normal,
                'portal_type': portal_type,
                'collection':  collection,
                'icon': icon,
                'size': size,
                'width': width,
                'height': height,
                'preview': preview,
                'sizes': sizes,
                'defscale': defscale,
                'media': media,
                'classes': classes,
                'title': title,
                'description': description,
                'linkable': linkable,
                'src': src,
                'anchor': anchor,
                'state': review_state,
                'class': className,
                }
        except Unauthorized:
            return None

    def info(self, brain, allowLink=True):
        '''Get information from a brain'''
        __traceback_info__ = (brain, allowLink)
        id = brain.getId
        url = brain.getURL()
        portal_type = brain.portal_type
        collection = portal_type in self.coll_types
        tool = self.tool
        preview = tool.getPreviewUrl(portal_type, url)

        # Path for the uid catalog doesn't have the leading '/'
        path = brain.getPath()
        UID = None
        if path and self.uid_catalog:
            try:
                metadata = self.uid_catalog.getMetadataForUID(path[self.prefix_length:])
            except KeyError:
                metadata = None
            if metadata:
                UID = metadata.get('UID', None)

        if UID:
            id = UID

        if collection and self.resource_type.allow_browse:
            src = brain.getURL()
            if not src.endswith('/'): src += '/'
            src += self.srctail
        else:
            src = None

        if UID and self.linkbyuid:
            url = self.base+'/resolveuid/%s' % UID

        if self.showimagesize:
            normal = tool.getNormalUrl(portal_type, url)
        else:
            normal = url

        sizes = self.get_image_sizes(brain, portal_type, url)
        defscale = self.tool.getDefaultScaleForType(portal_type)
        media = self.media(portal_type)
        classes = self.classes(portal_type)

        icon = self.icon(portal_type)
        size, width, height = self.sizes(brain)

        title = filterControlChars(brain.Title or brain.getId)
        description = newline_to_br(html_quote(brain.Description))
        linkable = None
        if allowLink:
            linkable = True
            collection = False

        anchor = portal_type in self.anchor_types
        review_state, className = self.getState(brain.review_state)

        return {
            'id': id,
            'url': normal,
            'portal_type': portal_type,
            'collection':  collection,
            'icon': icon,
            'size': size,
            'width': width,
            'height': height,
            'preview': preview,
            'sizes': sizes,
            'defscale': defscale,
            'media': media,
            'classes': classes,
            'title': title,
            'description': description,
            'linkable': linkable,
            'src': src,
            'anchor': anchor,
            'state': review_state,
            'class': className,
            }


class PloneDrawers:
    security = ClassSecurityInfo()

    security.declareProtected("View", "getPreviewable")
    def getPreviewable(self):
        """Returns previewable types and a possible preview path"""
        if HAS_PIL:
            def best_preview(field):
                sizes = getattr(field, 'sizes', None)
                if not sizes:
                    return field.getName()

                preview = None
                previewsize = (0,0)
                for k in sizes:
                    if previewsize < sizes[k] <= (128,128):
                        preview = k
                        previewsize = sizes[k]
                if not preview:
                    smallest = min(sizes.values())
                    for k in sizes:
                        if sizes[k]==smallest:
                            preview = k
                            break
                return "%s_%s" % (field.getName(), preview)

        else:
            def best_preview(field):
                return field.getName()

        result = []
        typestool = getToolByName(self, 'portal_types')
        archetype_tool = getToolByName(self, 'archetype_tool', None)
        if archetype_tool is None:
            return result
        valid = dict.fromkeys([t.getId() for t in typestool.listTypeInfo()])
        types = archetype_tool.listRegisteredTypes()
        for t in types:
            name = t['portal_type']
            if not name in valid:
                continue
            schema = t['schema']
            for field in schema.fields():
                if not isinstance(field, ImageField):
                    continue
                result.append((name, best_preview(field)))
                break
        return result
        
    security.declarePublic("getResourceType")
    def getResourceType(self, resource_type=None):
        """Convert resource type string to instance"""
        if isinstance(resource_type, ResourceType):
            return resource_type

        if not resource_type:
            resource_type = self.REQUEST.get('resource_type', 'mediaobject')

        return ResourceType(self, resource_type)

    security.declarePublic("getFolderItems")
    def getFolderItems(self, context, resource_type=None, portal=None):
        """List the contents of a folder"""
        resource_type = self.getResourceType(resource_type)
        collection_type = self.getResourceType('collection')
        coll_types = collection_type.portal_types
        link_types = resource_type.portal_types
        allow_browse = resource_type.allow_browse

        if portal is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()

        query = resource_type.getQuery()
        content =  context.getFolderContents(contentFilter=query)
        linkable = dict([(o.id,1) for o in content ])

        if allow_browse and coll_types:
            # Do an extended query which includes collections whether
            # or not they were matched by the first query,
            # and which also, unfortunately may include content which
            # doesn't match the original query.
            query2 = {}
            if link_types:
                query2['portal_type'] = tuple(link_types) + tuple(coll_types)
            else:
                query2['portal_type'] = ()

            if 'sort_on' in query:
                query2['sort_on'] = query['sort_on']

            allcontent = context.getFolderContents(contentFilter=query2)
            content = [c for c in allcontent
                if c.portal_type in coll_types or c.id in linkable ]

        link_types = query['portal_type']
        items = self.infoForBrains(content, resource_type, portal, linkids=linkable)

        if allow_browse and context is not portal:
            parent = context.aq_parent
            pt = getattr(parent, 'portal_type', None)
            if pt in collection_type.portal_types:
                data = self.getSingleObjectInfo(parent, resource_type)
                data['label'] = '.. (Parent folder)'
                items.insert(0, data)
        return items

    security.declarePublic("getSingleObjectInfo")
    def getSingleObjectInfo(self, context, resource_type=None, portal=None):
        """Return info for a single object"""
        if not resource_type: resource_type = self.getResourceType()
        if portal is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
        return self.infoForBrains([context], resource_type, portal)[0]

    security.declarePublic("getBreadCrumbs")
    def getBreadCrumbs(self, context, template):
        """Return breadcrumbs for drawer"""
        resource_type = self.getResourceType()
        if not resource_type.allow_browse:
            return []

        id = template.getId()
        putils = getToolByName(self, 'plone_utils')
        path = [ ("Home", getToolByName(self, 'portal_url')())]

        if getattr(putils.aq_base, 'createBreadCrumbs', None) is not None:
            path = path + [(x['Title'],x['absolute_url']) for x in putils.createBreadCrumbs(context)]
        else:
            path = path + self.breadcrumbs(context)[1:-1]

        # Last crumb should not be linked:
        path[-1] = (path[-1][0], None)

        crumbs = []
        for title,url in path:
            if url:
                url = self.kupuUrl("%s/%s" % (url.rstrip('/'), id))
            crumbs.append({'Title':title, 'absolute_url':url})

        return crumbs

    security.declareProtected('View','getCurrentObject')
    def getCurrentObject(self, portal=None):
        '''Returns object information for a selected object'''
        request = self.REQUEST
        if portal is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
        reference_tool = getToolByName(portal, 'reference_catalog')
        rt = self.getResourceType()
        portal_types = rt.portal_types
        src = request.get('src')
        # Remove any spurious query string or fragment
        for c in '#?':
            if c in src:
                src = src.split(c, 1)[0]

        match = UIDURL.match(src)

        if match:
            # src=http://someurl/resolveuid/<uid>
            uid = match.group(1)
            obj = reference_tool.lookupObject(uid)
            
        elif src and '://' in src:
            # src=http://someurl/somepath/someobject
            base = portal.absolute_url()
            if src.startswith(base):
                src = src[len(base):].lstrip('/')
            try:
                obj = portal.restrictedTraverse(src)
                if portal_types:
                    while not shasattr(obj.aq_base, 'portal_type'):
                        obj = obj.aq_parent
                    while obj.portal_type not in portal_types:
                        obj = obj.aq_parent
                        if obj is portal:
                            return []
            except (KeyError, AttributeError):
                return []
        else:
            # src=<uid1> <uid2> ... <uidn>
            src = src.split(' ') # src is a list of uids.
            objects = [ reference_tool.lookupObject(uid) for uid in src ]
            objects = [ o for o in objects if o is not None ]
            return objects

        if obj is None:
            return None
        return [obj]

    security.declarePublic("getCurrentParent")
    def getCurrentParent(self):
        """Find the parent of the object specified in the src string.
        If multiple objects and they don't have the same parent, or if no suitable object
        returns None, otherwise returns the parent."""
        objects = self.getCurrentObject()
        parent = None
        for obj in objects:
            if parent is not None and parent is not obj.aq_parent:
                return None
            parent = obj.aq_parent
        return parent

    security.declarePublic("getCurrentSelection")
    def getCurrentSelection(self, portal=None):
        '''Returns object information for a selected object'''
        objects = self.getCurrentObject(portal)
        return self.infoForBrains(objects, self.getResourceType(), portal)

    security.declarePublic("getMyItems")
    def getMyItems(self):
        request = self.REQUEST
        response = request.RESPONSE
        response.setHeader('Cache-Control', 'no-cache')

        member_tool = getToolByName(self, 'portal_membership')
        member = member_tool.getAuthenticatedMember()

        # the default resource type is mediaobject
        search_params = {}
        search_params['sort_on'] = 'modified'
        search_params['sort_order'] = 'reverse'
        search_params['limit'] = 20
        search_params['Creator'] = member.getMemberId()

        return self.infoForQuery(search_params)

    security.declarePublic("getRecentItems")
    def getRecentItems(self):
        search_params = {}
        search_params['sort_on'] = 'modified'
        search_params['sort_order'] = 'reverse'
        search_params['limit'] = 20
        search_params['review_state'] = 'visible', 'published'

        return self.infoForQuery(search_params)

    security.declarePublic("kupuSearch")
    def kupuSearch(self):
        request = self.REQUEST
        search_params = {}
        search_params.update(request.form)

        # Get the maximum number of results with 500 being the default and
        # absolute maximum.
        abs_max = 500
        search_params['limit'] = min(request.get('max_results', abs_max), abs_max)

        return self.infoForQuery(search_params)

    security.declareProtected("View", "infoForQuery")
    def infoForQuery(self, query, resource_type=None, portal=None):
        resource_type = self.getResourceType()
        if portal is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
        
        baseQuery = resource_type.getQuery()
        query.update(baseQuery)
        limit = query.get('limit', None)
        pt = query['portal_type']
        if not pt:
            del query['portal_type']
        catalog = getToolByName(portal, 'portal_catalog')
        values = catalog.searchResults(query)
        if limit:
            values = values[:limit]
        return self.infoForBrains(values, resource_type, portal)

    security.declareProtected("View", "infoForBrains")
    def infoForBrains(self, values, resource_type, portal=None, linkids=None):
        request = self.REQUEST
        response = request.RESPONSE
        response.setHeader('Cache-Control', 'no-cache')
        linktypes=resource_type.portal_types
        if portal is None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
        
        adaptor = InfoAdaptor(self, resource_type, portal)
        
        # For Plone 2.0.5 compatability, if getId is callable we assume
        # we have an object rather than a brains.
        if values and callable(values[0].getId):
            info = adaptor.info_object
        else:
            info = adaptor.info

        res = []

        for obj in values:
            portal_type = getattr(obj, 'portal_type', '')

            if linkids is not None:
                linkable = obj.id in linkids
            elif len(linktypes)==0:
                linkable = True
            else:
                linkable = portal_type in linktypes

            data = info(obj, linkable)
            if data:
                res.append(data)
        return res

    security.declareProtected("View", "canCaption")
    def canCaption(self, field):
        return (getattr(field, 'default_output_type', None) in
            ('text/x-html-safe', 'text/x-html-captioned'))

    security.declarePublic("getLabelFromWidget")
    def getLabelFromWidget(self, widget):
        """Get the label for a widget converting from i18n message if needed"""
        label = util.translate(widget.Label(self), self.REQUEST)
        if isinstance(label, str):
            label = label.decode('utf8', 'replace')
        return label

    security.declareProtected("View", "getKupuFields")
    def getKupuFields(self, filter=1):
        """Returns a list of all kupu editable fields"""
        inuse = getToolByName(self, 'portal_catalog').uniqueValuesFor('portal_type')
        for t,f,pt in self._getKupuFields():
            if html2captioned.sanitize_portal_type(pt) in inuse or not filter:
                yield dict(type=t, name=f.getName(), portal_type=pt,
                           label=self.getLabelFromWidget(f.widget))

    def _getKupuFields(self):
        """Yield all fields which are editable using kupu"""
        archetype_tool = getToolByName(self, 'archetype_tool', None)
        types = archetype_tool.listRegisteredTypes()
        for t in types:
            schema = t.get('schema')
            if schema:
                typename = getattr(t['klass'], 'archetype_name', t['portal_type'])
                for f in schema.fields():
                    w = f.widget
                    if isinstance(w, (RichWidget, VisualWidget)):
                        yield typename, f, t['portal_type']

    security.declareProtected("View", "supportedCaptioning")
    def supportedCaptioning(self):
        """Returns a list of document/fields which have support for captioning"""
        supported = [t+'/'+self.getLabelFromWidget(f.widget) for (t,f,pt) in self._getKupuFields() if self.canCaption(f) ]
        return str.join(', ', supported)

    security.declareProtected("View", "unsupportedCaptioning")
    def unsupportedCaptioning(self):
        """Returns a list of document/fields which do not have support for captioning"""
        unsupp = [t+'/'+self.getLabelFromWidget(f.widget) for (t,f,pt) in self._getKupuFields() if not self.canCaption(f) ]
        return str.join(', ', unsupp)

    security.declareProtected("View", "transformIsEnabled")
    def transformIsEnabled(self):
        """Test whether the output transform is enabled for x-html-safe"""
        uid_catalog = getToolByName(self, 'uid_catalog', None)
        portal_transforms = getToolByName(self, 'portal_transforms', None)
        if not uid_catalog or not portal_transforms:
            return False
        # Find something, anything which has a UID
        content = uid_catalog.searchResults(sort_on='', sort_limit=1)
        if not content:
            return False
        uid = content[0].UID # Get an arbitrary used UID.
        link = 'resolveuid/%s' % uid
        test = '<a href="%s"></a>' % link
        txfrm = portal_transforms.convertTo('text/x-html-safe', test, mimetype='text/html', context=self)
        if hasattr(txfrm, 'getData'):
            txfrm = txfrm.getData()
        return txfrm and not link in txfrm

    security.declareProtected("View", "isUploadSupported")
    def isUploadSupported(self, context):
        """Returns True if we can upload the the current folder."""
        resource_type = self.getResourceType()
        if resource_type.name != 'mediaobject':
            return False

        allowedContent = context.getAllowedTypes()
        allowed = dict.fromkeys([a.getId() for a in allowedContent])
        for t in resource_type.portal_types:
            if t in allowed:
                return True
        return False

    security.declareProtected("View", "getBaseUrl")
    def getBaseUrl(self, context, include_factory=False, resource_type=None):
        base = context.absolute_url()

        if resource_type:
            rt = self.getResourceType(resource_type);
            sd = rt.startup_directory
            if sd:
                base = sd

        posfactory = base.find('/portal_factory/')
        if posfactory>0:
            if include_factory:
                base = base[:posfactory+15]
            else:
                base = base[:posfactory]
        return base

    def _getImageSizes(self):
        resource_type = self.getResourceType()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        mediatypes = resource_type.get_portal_types()
        catalog = getToolByName(self, 'portal_catalog')
        adaptor = InfoAdaptor(self, resource_type, portal)

        sizes = {}
        for portal_type in mediatypes:
            brains = catalog.searchResults(portal_type=portal_type, limit=1)[:1]
            if brains:
                info = adaptor.get_image_sizes(brains[0], portal_type, '')
                if info:
                    for i in info:
                        sizes[i['uri']] = 1
        return sizes

    security.declareProtected("View", "convertUidsToPaths")
    def convertUidsToPaths(self, value=None):
        """Convert a list of uids
        (or a single space or newline separated string)
        to a list of paths"""
        uid_catalog = getToolByName(self, 'uid_catalog')
        ppath = getToolByName(self, 'portal_url').getPortalPath()[1:]+'/'
        
        if isinstance(value, basestring):
            value = value.split()
        if not value:
            return []
            
        brains = uid_catalog.searchResults(UID=value)
        paths = [ppath+b.getPath() for b in brains]
        return paths

InitializeClass(PloneDrawers)
