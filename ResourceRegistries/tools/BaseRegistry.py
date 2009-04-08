import random

# we *have* to use StringIO here, because we can't add attributes to cStringIO
# instances (needed in BaseRegistryTool.__getitem__).
from StringIO import StringIO

from App.Common import rfc1123_date
from DateTime import DateTime
from zExceptions import NotFound
from Globals import InitializeClass, Persistent, PersistentMapping
from AccessControl import ClassSecurityInfo, Unauthorized

from zope.interface import implements

from Acquisition import aq_base, aq_parent, aq_inner, ExplicitAcquisitionWrapper

from OFS.Image import File
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from OFS.Cache import Cacheable

from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.ResourceRegistries import permissions
from Products.ResourceRegistries.interfaces import IResourceRegistry

import Acquisition


# version agnostic import of z3_Resource
try:
    import Products.Five
except ImportError:
    __five__ = False
    from zope.app.publisher.browser.resource import Resource as z3_Resource
else:
    __five__ = True
    try:
        # Zope 2.8 / Five 1.0.2
        from Products.Five.resource import Resource as z3_Resource
        __five_pre_1_3_ = True
    except ImportError:
        # Zope 2.9 / Five 1.3
        from Products.Five.browser.resource import Resource as z3_Resource
        __five_pre_1_3__ = False



def getDummyFileForContent(name, ctype):
    # make output file like and add an headers dict, so the contenttype
    # is properly set in the headers
    output = StringIO()
    output.headers = {'content-type': ctype}
    return File(name, name, output)

def getCharsetFromContentType(contenttype, default='utf-8'):
    contenttype = contenttype.lower()
    if 'charset=' in contenttype:
        i = contenttype.index('charset=')
        charset = contenttype[i+8:]
        charset = charset.split(';')[0]
        return charset
    else:
        return default

class Resource(Persistent):
    security = ClassSecurityInfo()

    def __init__(self, id, **kwargs):
        self._data = PersistentMapping()
        self._data['id'] = id
        self._data['expression'] = kwargs.get('expression', '')
        self._data['enabled'] = kwargs.get('enabled', True)
        self._data['cookable'] = kwargs.get('cookable', True)
        self._data['cacheable'] = kwargs.get('cacheable', True)

    def copy(self):
        result = self.__class__(self.getId())
        for key, value in self._data.items():
            if key != 'id':
                result._data[key] = value
        return result

    security.declarePublic('getId')
    def getId(self):
        return self._data['id']

    def _setId(self, id):
        self._data['id'] = id

    security.declarePublic('getExpression')
    def getExpression(self):
        return self._data['expression']

    security.declareProtected(permissions.ManagePortal, 'setExpression')
    def setExpression(self, expression):
        self._data['expression'] = expression

    security.declarePublic('getEnabled')
    def getEnabled(self):
        return bool(self._data['enabled'])

    security.declareProtected(permissions.ManagePortal, 'setEnabled')
    def setEnabled(self, enabled):
        self._data['enabled'] = enabled

    security.declarePublic('getCookable')
    def getCookable(self):
        return self._data['cookable']

    security.declareProtected(permissions.ManagePortal, 'setCookable')
    def setCookable(self, cookable):
        self._data['cookable'] = cookable

    security.declarePublic('getCacheable')
    def getCacheable(self):
        # as this is a new property, old instance might not have that value, so
        # return True as default
        return self._data.get('cacheable', True)

    security.declareProtected(permissions.ManagePortal, 'setCacheable')
    def setCacheable(self, cacheable):
        self._data['cacheable'] = cacheable

InitializeClass(Resource)


class Skin(Acquisition.Implicit):
    security = ClassSecurityInfo()

    def __init__(self, skin):
        self._skin = skin

    def __before_publishing_traverse__(self, object, REQUEST):
        """ Pre-traversal hook. Specify the skin. 
        """
        self.changeSkin(self._skin, REQUEST)

    def __bobo_traverse__(self, REQUEST, name):
        """Traversal hook."""
        if REQUEST is not None and \
           self.concatenatedresources.get(name, None) is not None:
            parent = aq_parent(self)
            # see BaseTool.__bobo_traverse__
            deferred = getDummyFileForContent(name, self.getContentType())
            post_traverse = getattr(aq_base(REQUEST), 'post_traverse', None)
            if post_traverse is not None:
                post_traverse(parent.deferredGetContent, (deferred, name, self._skin))
            else:
                parent.deferredGetContent(deferred, name, self._skin)
            return deferred.__of__(parent)
        obj = getattr(self, name, None)
        if obj is not None:
            return obj
        raise AttributeError('%s' % (name,))

InitializeClass(Skin)


class BaseRegistryTool(UniqueObject, SimpleItem, PropertyManager, Cacheable):
    """Base class for a Plone registry managing resource files."""

    security = ClassSecurityInfo()
    implements(IResourceRegistry)
    __implements__ = SimpleItem.__implements__
    manage_options = SimpleItem.manage_options

    attributes_to_compare = ('getExpression', 'getCookable', 'getCacheable')
    filename_base = 'ploneResources'
    filename_appendix = '.res'
    merged_output_prefix = u''
    cache_duration = 3600
    resource_class = Resource

    debugmode = False
    autogroupingmode = False

    #
    # Private Methods
    #

    def __init__(self):
        """Add the storages."""
        self.resources = ()
        self.cookedresources = ()
        self.concatenatedresources = {}
        self.debugmode = False
        self.autogroupingmode = False

    def __getitem__(self, item):
        """Return a resource from the registry."""
        original = self.REQUEST.get('original', False)
        output = self.getResourceContent(item, self, original)
        contenttype = self.getContentType()
        return (output, contenttype)

    def deferredGetContent(self, deferred, name, skin=None):
        """ uploads data of a resource to deferred """
        # "deferred" was previosly created by a getDummyFileForContent
        # call in the __bobo_traverse__ method. As the name suggests,
        # the file is merely a traversable dummy with appropriate
        # headers and name. Now as soon as REQUEST.traverse
        # finishes and gets to the part where it calls the tuples
        # register using post_traverse (that's actually happening
        # right now) we can be sure, that all necessary security
        # stuff has taken place (e.g. authentication).
        kw = {'skin':skin,'name':name}
        data = None
        duration = self.cache_duration  # duration in seconds
        if not self.getDebugMode() and self.isCacheable(name):
            if self.ZCacheable_isCachingEnabled():
                data = self.ZCacheable_get(keywords=kw)
            if data is None:
                # This is the part were we would fail if
                # we would just return the ressource
                # without using the post_traverse hook:
                # self.__getitem__ leads (indirectly) to
                # a restrictedTraverse call which performs
                # security checks. So if a tool (or its ressource)
                # is not "View"able by anonymous - we'd
                # get an Unauthorized exception.
                data = self.__getitem__(name)
                self.ZCacheable_set(data, keywords=kw)
        else:
            data = self.__getitem__(name)
            duration = 0

        output, contenttype = data

        seconds = float(duration)*24.0*3600.0
        response = self.REQUEST.RESPONSE
        response.setHeader('Expires',rfc1123_date((DateTime() + duration).timeTime()))
        response.setHeader('Cache-Control', 'max-age=%d' % int(seconds))

        if isinstance(output, unicode):
            portal_props = getToolByName(self, 'portal_properties')
            site_props = portal_props.site_properties
            charset = site_props.getProperty('default_charset', 'utf-8')
            output = output.encode(charset)
            if 'charset=' not in contenttype:
                contenttype += ';charset=' + charset
        
        out = StringIO(output)
        out.headers = {'content-type': contenttype}
        # At this point we are ready to provide some content
        # for our dummy and since it's just a File instance,
        # we can "upload" (a quite delusive method name) the
        # data and that's it.
        deferred.manage_upload(out)
    
    def __bobo_traverse__(self, REQUEST, name):
        """Traversal hook."""
        # First see if it is a skin
        skintool = getToolByName(self, 'portal_skins')
        skins = skintool.getSkinSelections()
        if name in skins:
            return Skin(name).__of__(self)

        
        if REQUEST is not None and \
           self.concatenatedresources.get(name, None) is not None:
            # __bobo_traverse__ is called before the authentication has
            # taken place, so if some operations require an authenticated
            # user (like restrictedTraverse in __getitem__) it will fail.
            # Now we can circumvent that by using the post_traverse()
            # method from BaseRequest. It temporarely stores a callable
            # along with its arguments in a REQUEST instance and calls
            # them at the end of BaseRequest.traverse()
            deferred = getDummyFileForContent(name, self.getContentType())
            # __bobo_traverse__ might be called from within
            # OFS.Traversable.Traversable.unrestrictedTraverse()
            # which passes a simple dict to the method, instead
            # of a "real" REQUEST object
            post_traverse = getattr(aq_base(REQUEST), 'post_traverse', None)
            if post_traverse is not None:
                post_traverse(self.deferredGetContent, (deferred, name, None))
            else:
                self.deferredGetContent(deferred, name, None)
            return deferred.__of__(self)
        obj = getattr(self, name, None)
        if obj is not None:
            return obj
        raise AttributeError('%s' % (name,))

    security.declarePublic('isCacheable')
    def isCacheable(self, name):
        """Return a boolean whether the resource is cacheable or not."""
        resource_id = self.concatenatedresources.get(name, [None])[0]
        if resource_id is None:
            return False
        resources = self.getResourcesDict()
        resource = resources.get(resource_id, None)
        result = resource.getCacheable()
        return result

    security.declarePrivate('validateId')
    def validateId(self, id, existing):
        """Safeguard against duplicate ids."""
        for sheet in existing:
            if sheet.getId() == id:
                raise ValueError, 'Duplicate id %s' %(id)

    security.declarePrivate('storeResource')
    def storeResource(self, resource, skipCooking=False):
        """Store a resource."""
        self.validateId(resource.getId(), self.getResources())
        resources = list(self.resources)
        resources.append(resource)
        self.resources = tuple(resources)
        if not skipCooking:
            self.cookResources()

    security.declarePrivate('clearResources')
    def clearResources(self):
        """Clears all resource data.

        Convenience funtion for Plone migrations and tests.
        """
        self.resources = ()
        self.cookedresources = ()
        self.concatenatedresources = {}

    security.declarePrivate('getResourcesDict')
    def getResourcesDict(self):
        """Get the resources as a dictionary instead of an ordered list.

        Good for lookups. Internal.
        """
        resources = self.getResources()
        d = {}
        for s in resources:
            d[s.getId()] = s
        return d

    security.declarePrivate('compareResources')
    def compareResources(self, s1, s2):
        """Check if two resources are compatible."""
        for attr in self.attributes_to_compare:
            if getattr(s1, attr)() != getattr(s2, attr)():
                return False
        return True

    security.declarePrivate('sortResources')
    def sortResourceKey(self, resource):
        """Returns a sort key for the resource."""
        return [getattr(resource, attr)() for attr in
                self.attributes_to_compare]

    security.declarePrivate('generateId')
    def generateId(self, res_id, prev_id=None):
        """Generate a random id."""
        id_parts = res_id.split('.')
        if (len(id_parts) > 1):
            base = '.'.join(id_parts[:-1])
            appendix = ".%s" % id_parts[-1]
        else:
            base = id_parts[0]
            appendix = self.filename_appendix
        base = base.replace('++', '').replace('/', '')
        return '%s-cachekey%04d%s' % (base, random.randint(0, 9999), appendix)

    security.declarePrivate('finalizeResourceMerging')
    def finalizeResourceMerging(self, resource, previtem):
        """Finalize the resource merging with the previous item.

        Might be overwritten in subclasses.
        """
        pass

    security.declarePrivate('finalizeContent')
    def finalizeContent(self, resource, content):
        """Finalize the resource content.

        Might be overwritten in subclasses.
        """
        return content

    security.declareProtected(permissions.ManagePortal, 'cookResources')
    def cookResources(self):
        """Cook the stored resources."""
        if self.ZCacheable_isCachingEnabled():
            self.ZCacheable_invalidate()
        resources = [r.copy() for r in self.getResources() if r.getEnabled()]
        self.concatenatedresources = {}
        self.cookedresources = ()
        if self.getDebugMode():
            results = [x for x in resources]
        else:
            results = []
            if self.getAutoGroupingMode():
                # Sort resources according to their sortkey first, so resources
                # with compatible keys will be merged.
                def _sort_position(r):
                    key = self.sortResourceKey(r[0])
                    key.append(r[1])
                    return key
                # We need to respect the resource position inside the sort groups
                positioned_resources = [(r, resources.index(r)) for r in resources]
                positioned_resources.sort(key=_sort_position)
                resources = [r[0] for r in positioned_resources]
            for resource in resources:
                if results:
                    previtem = results[-1]
                    if resource.getCookable() and previtem.getCookable() \
                           and self.compareResources(resource, previtem):
                        res_id = resource.getId()
                        prev_id = previtem.getId()
                        self.finalizeResourceMerging(resource, previtem)
                        if self.concatenatedresources.has_key(prev_id):
                            self.concatenatedresources[prev_id].append(res_id)
                        else:
                            magic_id = self.generateId(res_id, prev_id)
                            self.concatenatedresources[magic_id] = [prev_id, res_id]
                            previtem._setId(magic_id)
                    else:
                        if resource.getCookable() or resource.getCacheable():
                            magic_id = self.generateId(resource.getId())
                            self.concatenatedresources[magic_id] = [resource.getId()]
                            resource._setId(magic_id)
                        results.append(resource)
                else:
                    if resource.getCookable() or resource.getCacheable():
                        magic_id = self.generateId(resource.getId())
                        self.concatenatedresources[magic_id] = [resource.getId()]
                        resource._setId(magic_id)
                    results.append(resource)

        resources = self.getResources()
        for resource in resources:
            self.concatenatedresources[resource.getId()] = [resource.getId()]
        self.cookedresources = tuple(results)

    security.declarePrivate('evaluateExpression')
    def evaluateExpression(self, expression, context):
        """Evaluate an object's TALES condition to see if it should be
        displayed.
        """
        try:
            if expression and context is not None:
                portal = getToolByName(context, 'portal_url').getPortalObject()

                # Find folder (code courtesy of CMFCore.ActionsTool)
                if context is None or not hasattr(context, 'aq_base'):
                    folder = portal
                else:
                    folder = context
                    # Search up the containment hierarchy until we find an
                    # object that claims it's PrincipiaFolderish.
                    while folder is not None:
                        if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                            # found it.
                            break
                        else:
                            folder = aq_parent(aq_inner(folder))

                __traceback_info__ = (folder, portal, context, expression)
                ec = createExprContext(folder, portal, context)
                return Expression(expression)(ec)
            else:
                return 1
        except AttributeError:
            return 1

    security.declareProtected(permissions.ManagePortal, 'getResource')
    def getResource(self, id):
        """Get resource object by id.
        
        If any property of the resource is changed, then cookResources of the
        registry must be called."""
        resources = self.getResourcesDict()
        resource = resources.get(id, None)
        if resource is not None:
            return ExplicitAcquisitionWrapper(resource, self)
        return None

    security.declarePrivate('getResourceContent')
    def getResourceContent(self, item, context, original=False):
        """Fetch resource content for delivery."""
        ids = self.concatenatedresources.get(item, None)
        resources = self.getResourcesDict()
        if ids is not None:
            ids = ids[:]
        output = u""
        if len(ids) > 1:
            output = output + self.merged_output_prefix

        portal = getToolByName(context, 'portal_url').getPortalObject()

        if context == self and portal is not None:
            context = portal

        portal_props = getToolByName(self, 'portal_properties')
        site_props = portal_props.site_properties
        default_charset = site_props.getProperty('default_charset', 'utf-8')

        for id in ids:
            try:
                if portal is not None:
                    obj = context.restrictedTraverse(id)
                else:
                    #Can't do anything other than attempt a getattr
                    obj = getattr(context, id)
            except (AttributeError, KeyError):
                output += u"\n/* XXX ERROR -- could not find '%s'*/\n" % id
                content = u''
                obj = None
            except Unauthorized:
                #If we're just returning a single resource, raise an Unauthorized,
                #otherwise we're merging resources in which case just log an error
                if len(ids) > 1:
                    #Object probably isn't published yet
                    output += u"\n/* XXX ERROR -- access to '%s' not authorized */\n" % id
                    content = u''
                    obj = None
                else:
                    raise

            if obj is not None:
                if isinstance(obj, z3_Resource):
                    # z3 resources
                    # XXX this is a temporary solution, we wrap the five resources
                    # into our mechanism, where it should be the other way around.
                    #
                    # First thing we must be aware of: resources give a complete
                    # response so first we must save the headers.
                    # Especially, we must delete the If-Modified-Since, because
                    # otherwise we might get a 30x response status in some cases.
                    response_headers = self.REQUEST.RESPONSE.headers.copy()
                    if_modif = self.REQUEST.get_header('If-Modified-Since', None)
                    try:
                        del self.REQUEST.environ['IF_MODIFIED_SINCE']
                    except KeyError:
                        pass
                    try:
                        del self.REQUEST.environ['HTTP_IF_MODIFIED_SINCE']
                    except KeyError:
                        pass
                    # Now, get the content.
                    content = obj.GET()
                    contenttype = self.REQUEST.RESPONSE.headers.get('content-type', '')
                    contenttype = getCharsetFromContentType(contenttype, default_charset)
                    content = unicode(content, contenttype)
                    # Now restore the headers and for safety, check that we
                    # have a 20x response. If not, we have a problem and
                    # some browser would hang indefinitely at this point.
                    assert int(self.REQUEST.RESPONSE.getStatus()) / 100 == 2
                    self.REQUEST.environ['HTTP_IF_MODIFIED_SINCE'] = if_modif
                    self.REQUEST.RESPONSE.headers = response_headers
                elif hasattr(aq_base(obj),'meta_type') and  obj.meta_type in ['DTML Method', 'Filesystem DTML Method']:
                    content = obj(client=self.aq_parent, REQUEST=self.REQUEST,
                                  RESPONSE=self.REQUEST.RESPONSE)
                    contenttype = self.REQUEST.RESPONSE.headers.get('content-type', '')
                    contenttype = getCharsetFromContentType(contenttype, default_charset)
                    content = unicode(content, contenttype)
                elif hasattr(aq_base(obj),'meta_type') and obj.meta_type == 'Filesystem File':
                    obj._updateFromFS()
                    content = obj._readFile(0)
                    contenttype = getCharsetFromContentType(obj.content_type, default_charset)
                    content = unicode(content, contenttype)
                elif hasattr(aq_base(obj),'meta_type') and obj.meta_type == 'ATFile':
                    f = obj.getFile()
                    contenttype = getCharsetFromContentType(f.getContentType(), default_charset)
                    content = unicode(str(f), contenttype)
                # We should add more explicit type-matching checks
                elif hasattr(aq_base(obj), 'index_html') and callable(obj.index_html):
                    content = obj.index_html(self.REQUEST,
                                             self.REQUEST.RESPONSE)
                    if not isinstance(content, unicode):
                        content = unicode(content, default_charset)
                elif callable(obj):
                    content = obj(self.REQUEST, self.REQUEST.RESPONSE)
                    if not isinstance(content, unicode):
                        content = unicode(content, default_charset)
                else:
                    content = str(obj)
                    content = unicode(content, default_charset)

            # Add start/end notes to the resource for better
            # understanding and debugging
            if content:
                output += u'\n/* - %s - */\n' % (id,)
                if original:
                    output += content
                else:
                    output += self.finalizeContent(resources[id], content)
                output += u'\n'
        return output

    #
    # ZMI Methods
    #

    security.declareProtected(permissions.ManagePortal, 'moveResourceUp')
    def moveResourceUp(self, id, steps=1, REQUEST=None):
        """Move the resource up 'steps' number of steps."""
        index = self.getResourcePosition(id)
        self.moveResource(id, index - steps)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'moveResourceDown')
    def moveResourceDown(self, id, steps=1, REQUEST=None):
        """Move the resource down 'steps' number of steps."""
        index = self.getResourcePosition(id)
        self.moveResource(id, index + steps)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'moveResourceToTop')
    def moveResourceToTop(self, id, REQUEST=None):
        """Move the resource to the first position."""
        self.moveResource(id, 0)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'moveResourceToBottom')
    def moveResourceToBottom(self, id, REQUEST=None):
        """Move the resource to the last position."""
        self.moveResource(id, len(self.resources))
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'moveResourceBefore')
    def moveResourceBefore(self, id, dest_id, REQUEST=None):
        """Move the resource before the resource with dest_id."""
        index = self.getResourcePosition(id)
        dest_index = self.getResourcePosition(dest_id)
        if index < dest_index:
            self.moveResource(id, dest_index - 1)
        else:
            self.moveResource(id, dest_index)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'moveResourceAfter')
    def moveResourceAfter(self, id, dest_id, REQUEST=None):
        """Move the resource after the resource with dest_id."""
        index = self.getResourcePosition(id)
        dest_index = self.getResourcePosition(dest_id)
        if index < dest_index:
            self.moveResource(id, dest_index)
        else:
            self.moveResource(id, dest_index + 1)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    #
    # Protected Methods
    #

    security.declareProtected(permissions.ManagePortal, 'registerResource')
    def registerResource(self, id, expression='', enabled=True,
                         cookable=True, cacheable=True):
        """Register a resource."""
        resource = Resource(id,
                            expression=expression,
                            enabled=enabled,
                            cookable=cookable,
                            cacheable=cacheable)
        self.storeResource(resource)

    security.declareProtected(permissions.ManagePortal, 'unregisterResource')
    def unregisterResource(self, id):
        """Unregister a registered resource."""
        resources = [item for item in self.getResources()
                     if item.getId() != id]
        self.resources = tuple(resources)
        self.cookResources()

    security.declareProtected(permissions.ManagePortal, 'renameResource')
    def renameResource(self, old_id, new_id):
        """Change the id of a registered resource."""
        self.validateId(new_id, self.getResources())
        resources = list(self.resources)
        for resource in resources:
            if resource.getId() == old_id:
                resource._setId(new_id)
                break
        self.resources = tuple(resources)
        self.cookResources()

    security.declareProtected(permissions.ManagePortal, 'getResourceIds')
    def getResourceIds(self):
        """Return the ids of all resources."""
        return tuple([x.getId() for x in self.getResources()])

    security.declareProtected(permissions.ManagePortal, 'getResources')
    def getResources(self):
        """Get all the registered resource data, uncooked.

        For management screens.
        """
        result = []
        for item in self.resources:
            if isinstance(item, dict):
                # BBB we used dicts before
                item = item.copy()
                item_id = item['id']
                del item['id']
                obj = self.resource_class(item_id, **item)
                result.append(obj)
            else:
                result.append(item)
        return tuple(result)

    security.declareProtected(permissions.ManagePortal, 'getCookedResources')
    def getCookedResources(self):
        """Get the cooked resource data."""
        result = []
        for item in self.cookedresources:
            if isinstance(item, dict):
                # BBB we used dicts before
                item = item.copy()
                item_id = item['id']
                del item['id']
                obj = self.resource_class(item_id, **item)
                result.append(obj)
            else:
                result.append(item)
        return tuple(result)

    security.declareProtected(permissions.ManagePortal, 'moveResource')
    def moveResource(self, id, position):
        """Move a registered resource to the given position."""
        index = self.getResourcePosition(id)
        if index == position:
            return
        elif position < 0:
            position = 0
        resources = list(self.getResources())
        resource = resources.pop(index)
        resources.insert(position, resource)
        self.resources = tuple(resources)
        self.cookResources()

    security.declareProtected(permissions.ManagePortal, 'getResourcePosition')
    def getResourcePosition(self, id):
        """Get the position (order) of an resource given its id."""
        resource_ids = list(self.getResourceIds())
        try:
            return resource_ids.index(id)
        except ValueError:
            raise NotFound, 'Resource %s was not found' % str(id)

    security.declareProtected(permissions.ManagePortal, 'getDebugMode')
    def getDebugMode(self):
        """Is resource merging disabled?"""
        return self.debugmode

    security.declareProtected(permissions.ManagePortal, 'setDebugMode')
    def setDebugMode(self, value):
        """Set whether resource merging should be disabled."""
        self.debugmode = value
        self.cookResources()

    security.declareProtected(permissions.ManagePortal, 'getAutoGroupingMode')
    def getAutoGroupingMode(self):
        """Is resource merging disabled?"""
        return self.autogroupingmode

    security.declareProtected(permissions.ManagePortal, 'setAutoGroupingMode')
    def setAutoGroupingMode(self, value):
        """Set whether resource merging should be disabled."""
        self.autogroupingmode = bool(value)
        self.cookResources()

    security.declareProtected(permissions.View, 'getEvaluatedResources')
    def getEvaluatedResources(self, context):
        """Return the filtered evaluated resources."""
        results = self.getCookedResources()

        # filter results by expression
        results = [item for item in results
                   if self.evaluateExpression(item.getExpression(), context)]

        return results

    security.declareProtected(permissions.View, 'getInlineResource')
    def getInlineResource(self, item, context):
        """Return a resource as inline code, not as a file object.

        Needs to take care not to mess up http headers.
        """
        headers = self.REQUEST.RESPONSE.headers.copy()
        # Save the RESPONSE headers
        output = self.getResourceContent(item, context)
        # File objects and other might manipulate the headers,
        # something we don't want. we set the saved headers back
        self.REQUEST.RESPONSE.headers = headers
        # This should probably be solved a cleaner way
        return str(output)

    security.declareProtected(permissions.View, 'getContentType')
    def getContentType(self):
        """Return the registry content type.

        Should be overwritten by subclasses.
        """
        return 'text/plain'

