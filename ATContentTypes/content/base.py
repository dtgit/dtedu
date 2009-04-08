#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""

"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'


import os
import posixpath
import logging
import transaction

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import BaseContent
    from Products.LinguaPlone.public import BaseFolder
    from Products.LinguaPlone.public import OrderedBaseFolder
    from Products.LinguaPlone.public import BaseBTreeFolder
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import BaseContent
    from Products.Archetypes.atapi import BaseFolder
    from Products.Archetypes.atapi import OrderedBaseFolder
    from Products.Archetypes.atapi import BaseBTreeFolder
    from Products.Archetypes.atapi import registerType

from AccessControl import ClassSecurityInfo, Permissions
from ComputedAttribute import ComputedAttribute
from Globals import InitializeClass
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Globals import REPLACEABLE
from webdav.Lockable import ResourceLockedError
from webdav.NullResource import NullResource
from zExceptions import MethodNotAllowed
from zExceptions import NotFound
from ZODB.POSException import ConflictError

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ManageProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone.PloneFolder import ReplaceableWrapper

from Products.ATContentTypes import permission as ATCTPermissions
from Products.ATContentTypes.config import MIME_ALIAS
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixin
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer

DEBUG = True
LOG = logging.getLogger('ATCT')

def registerATCT(class_, project):
    """Registers an ATContentTypes based type

    One reason to use it is to hide the lingua plone related magic.
    """
    assert IATContentType.isImplementedByInstancesOf(class_)
    registerType(class_, project)

def cleanupFilename(filename, request=None):
    """Removes bad chars from file names to make them a good id
    """
    if not filename:
        return
    if request is not None:
        return IUserPreferredFileNameNormalizer(request).normalize(filename)
    return None

def translateMimetypeAlias(alias):
    """Maps old CMF content types to real mime types
    """
    if alias.find('/') != -1:
        mime = alias
    else:
        mime = MIME_ALIAS.get(alias, None)
    assert(mime) # shouldn't be empty
    return mime


class ATCTMixin(BrowserDefaultMixin):
    """Mixin class for AT Content Types"""

    schema         =  ATContentTypeSchema

    archetype_name = 'AT Content Type'
    _atct_newTypeFor = {'portal_type' : None, 'meta_type' : None}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    # flag to show that the object is a temporary object
    isDocTemp = False
    _at_rename_after_creation = True # rename object according to the title?

    __implements__ = (IATContentType, BrowserDefaultMixin.__implements__)

    security       = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent,
                              'initializeArchetype')
    def initializeArchetype(self, **kwargs):
        """called by the generated add* factory in types tool

        Overwritten to call edit() instead of update() to have the cmf
        compatibility method.
        """
        try:
            self.initializeLayers()
            self.markCreationFlag()
            self.setDefaults()
            if kwargs:
                self.edit(**kwargs)
            self._signature = self.Schema().signature()
            if self.isPrincipiaFolderish:
                self.copyLayoutFromParent()
        except ConflictError:
            raise
        except Exception, msg:
            LOG.warn('Exception in initializeArchetype', exc_info=True)
            if DEBUG and str(msg) not in ('SESSION',):
                # debug code
                raise

    security.declarePrivate('copyLayoutFromParent')
    def copyLayoutFromParent(self):
        """Copies the layout from the parent object if it's of the same type."""
        parent = aq_parent(aq_inner(self))
        if parent is not None:
            # Only set the layout if we are the same type as out parent object
            if parent.meta_type == self.meta_type:
                # If the parent is the same type as us it should implement
                # BrowserDefaultMixin
                parent_layout = parent.getLayout()
                # Just in case we should make sure that the layout is
                # available to the new object
                if parent_layout in [l[0] for l in self.getAvailableLayouts()]:
                    self.setLayout(parent_layout)

    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, *args, **kwargs):
        """Reimplementing edit() to have a compatibility method for the old
        cmf edit() method
        """
        if len(args) != 0:
            # use cmf edit method
            return self.cmf_edit(*args, **kwargs)

        # if kwargs is containing a key that is also in the list of cmf edit
        # keywords then we have to use the cmf_edit comp. method
        cmf_edit_kws = getattr(aq_inner(self).aq_explicit, 'cmf_edit_kws', ())
        for kwname in kwargs.keys():
            if kwname in cmf_edit_kws:
                return self.cmf_edit(**kwargs)
        # standard AT edit - redirect to update()
        return self.update(**kwargs)

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, *args, **kwargs):
        """Overwrite this method to make AT compatible with the crappy
        CMF edit()
        """
        raise NotImplementedError("cmf_edit method isn't implemented")

    def exclude_from_nav(self):
        """Accessor for excludeFromNav field
        """
        field = self.getField('excludeFromNav')
        if field is not None:
            return field.get(self)
        else:
            return False

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ZMI / Plone get size method
        """
        f = self.getPrimaryField()
        if f is None:
            return 0
        return f.get_size(self) or 0

InitializeClass(ATCTMixin)

class ATCTContent(ATCTMixin, BaseContent):
    """Base class for non folderish AT Content Types"""

    __implements__ = (BaseContent.__implements__,
                      ATCTMixin.__implements__)

    security       = ClassSecurityInfo()

    security.declarePrivate('manage_afterPUT')
    def manage_afterPUT(self, data, marshall_data, file, context, mimetype,
                        filename, REQUEST, RESPONSE):
        """After webdav/ftp PUT method

        Set title according to the id on webdav/ftp PUTs.
        """
        id = self.getId()
        title = self.Title()
        if not title:
            # Use the last-segment from the url as the id, as the
            # object might have been renamed somehow (eg: by id
            # mangling).
            request = REQUEST or getattr(self, 'REQUEST', None)
            if request is not None:
                path_info = request.get('PATH_INFO')
                if path_info:
                    id = posixpath.basename(path_info)
            self.setTitle(id)

InitializeClass(ATCTContent)

class ATCTFileContent(ATCTContent):
    """Base class for content types containing a file like ATFile or ATImage

    The file field *must* be the exclusive primary field
    """

    # the precondition attribute is required to make ATFile and
    # ATImage compatible with OFS.Image.*. The precondition feature is
    # (not yet) supported.
    precondition = ''

    manage_options = (
        ATCTContent.manage_options[0:1] +
        ATCTContent.manage_options[2:]
        )

    security = ClassSecurityInfo()

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file (use default index_html)
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getPrimaryField()
        return field.download(self, REQUEST, RESPONSE)

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Make it directly viewable when entering the objects URL
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getPrimaryField()
        data  = field.getAccessor(self)(REQUEST=REQUEST, RESPONSE=RESPONSE)
        if data:
            return data.index_html(REQUEST, RESPONSE)
        # XXX what should be returned if no data is present?

    security.declareProtected(View, 'get_data')
    def get_data(self):
        """CMF compatibility method
        """
        data = aq_base(self.getPrimaryField().getAccessor(self)())
        return str(getattr(data, 'data', data))

    data = ComputedAttribute(get_data, 1)

    security.declareProtected(View, 'size')
    def size(self):
        """Get size (image_view.pt)
        """
        return self.get_size()

    security.declareProtected(View, 'get_content_type')
    def get_content_type(self):
        """CMF compatibility method
        """
        f = self.getPrimaryField().getAccessor(self)()
        return f and f.getContentType() or 'text/plain' #'application/octet-stream'

    content_type = ComputedAttribute(get_content_type, 1)

    security.declarePrivate('update_data')
    def update_data(self, data, content_type=None, size='ignored'):
        kwargs = {}
        if content_type is not None:
            kwargs['mimetype'] = content_type
        mutator = self.getPrimaryField().getMutator(self)
        mutator(data, **kwargs)

    security.declareProtected(ModifyPortalContent, 'manage_edit')
    def manage_edit(self, title, content_type, precondition='',
                    filedata=None, REQUEST=None):
        """
        Changes the title and content type attributes of the File or Image.
        """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        self.setTitle(title)
        if filedata is not None:
            self.update_data(filedata, content_type, len(filedata))
        if REQUEST:
            message="Saved changes."
            return self.manage_main(self,REQUEST,manage_tabs_message=message)

    def _cleanupFilename(self, filename, request=None):
        """Cleans the filename from unwanted or evil chars
        """
        if filename and not isinstance(filename, unicode):
            encoding = self.getCharset()
            filename = unicode(filename, encoding)

        filename = cleanupFilename(filename, request=request)
        return filename and filename.encode(encoding) or None

    def _setATCTFileContent(self, value, **kwargs):
        """Set id to uploaded id
        """
        field = self.getPrimaryField()
        # set first then get the filename
        field.set(self, value, **kwargs) # set is ok
        if self._isIDAutoGenerated(self.getId()):
            filename = field.getFilename(self, fromBaseUnit=False)
            request = self.REQUEST
            clean_filename = self._cleanupFilename(filename, request=request)
            request_id = request.form.get('id')
            if request_id and not self._isIDAutoGenerated(request_id):
                # request contains an id
                # skip renaming when then request id is not autogenerated which
                # means the user has defined an id. It's autogenerated when the
                # the user has disabled "short name editing".
                return
            elif clean_filename == self.getId():
                # destination id and old id are equal
                return
            elif clean_filename:
                # got a clean file name - rename it
                # apply subtransaction. w/o a subtransaction renaming
                # fails when the type is created using portal_factory
                transaction.savepoint(optimistic=True)
                self.setId(clean_filename)

    security.declareProtected(View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        """Validates upload file and id
        """
        id     = REQUEST.form.get('id')
        field  = self.getPrimaryField()
        f_name = field.getName()
        upload = REQUEST.form.get('%s_file' % f_name, None)
        filename = getattr(upload, 'filename', None)
        if isinstance(filename, basestring):
            filename = os.path.basename(filename)
            filename = filename.split("\\")[-1]
        clean_filename = self._cleanupFilename(filename, request=REQUEST)
        used_id = (id and not self._isIDAutoGenerated(id)) and id or clean_filename

        if upload:
            # the file may have already been read by a
            # former method
            upload.seek(0)

        if not used_id:
            return

        if getattr(self, 'check_id', None) is not None:
            check_id = self.check_id(used_id,required=1)
        else:
            # If check_id is not available just look for conflicting ids
            parent = aq_parent(aq_inner(self))
            check_id = used_id in parent.objectIds() and \
                       'Id %s conflicts with an existing item'% used_id or False
        if check_id and used_id == id:
            errors['id'] = check_id
            REQUEST.form['id'] = used_id
        elif check_id:
            errors[f_name] = check_id

    security.declarePrivate('manage_afterPUT')
    def manage_afterPUT(self, data, marshall_data, file, context, mimetype,
                        filename, REQUEST, RESPONSE):
        """After webdav/ftp PUT method

        Set the title according to the uploaded filename if the title
        is empty or set it to the id if no filename is given.
        """
        id = self.getId()
        title = self.Title()
        if not title:
            if filename:
                self.setTitle(filename)
            else:
                # Use the last-segment from the url as the id, as the
                # object might have been renamed somehow (eg: by id
                # mangling).
                request = REQUEST or getattr(self, 'REQUEST', None)
                if request is not None:
                    path_info = request.get('PATH_INFO')
                    if path_info:
                        id = posixpath.basename(path_info)
                self.setTitle(id)

InitializeClass(ATCTFileContent)


class ATCTFolder(ATCTMixin, BaseFolder):
    """Base class for folderish AT Content Types (but not for folders)

    DO NOT USE this base class for folders but only for folderish objects like
    AT Topic. It doesn't support constrain types!
    """

    __implements__ = (ATCTMixin.__implements__,
                      BaseFolder.__implements__)

    security       = ClassSecurityInfo()

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """Returns 1 as folders have no size."""
        return 1

InitializeClass(ATCTFolder)


class ATCTFolderMixin(ConstrainTypesMixin, ATCTMixin):
    """ Constrained folderish type """

    __implements__ = (ATCTMixin.__implements__,
                      ConstrainTypesMixin.__implements__,)

    security       = ClassSecurityInfo()

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead
        of index_html """
        return getToolByName(self, 'plone_utils').browserDefault(self)

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """Returns 1 as folders have no size."""
        return 1

    security.declarePrivate('manage_afterMKCOL')
    def manage_afterMKCOL(self, id, result, REQUEST=None, RESPONSE=None):
        """After MKCOL handler

        Set title according to the id
        """
        # manage_afterMKCOL is called in the context of the parent
        # folder, *not* in the context of the new folder!
        new = getattr(self, id)
        title = new.Title()
        if not title.strip():
            # Use the last-segment from the url as the id, as the
            # object might have been renamed somehow (eg: by id
            # mangling).
            request = REQUEST or getattr(self, 'REQUEST', None)
            if request is not None:
                path_info = request.get('PATH_INFO')
                if path_info:
                    id = posixpath.basename(path_info)
            new.update(title=id)

    security.declareProtected(View, 'HEAD')
    def HEAD(self, REQUEST, RESPONSE):
        """Overwrite HEAD method for HTTP HEAD requests

        Returns 404 Not Found if the default view can't be acquired or 405
        Method not allowed if the default view has no HEAD method.
        """
        view_id = self.getDefaultPage() or self.getLayout()
        view_method = getattr(self, view_id, None)
        if view_method is None:
            # view method couldn't be acquired
            raise NotFound, "View method %s for requested resource is not " \
                             "available." % view_id
        if getattr(aq_base(view_method), 'HEAD', None) is not None:
            # view method has a HEAD method
            return view_method.__of__(self).HEAD(REQUEST, RESPONSE)
        else:
            raise MethodNotAllowed, 'Method not supported for this resource.'

InitializeClass(ATCTFolderMixin)


class ATCTOrderedFolder(ATCTFolderMixin, OrderedBaseFolder):
    """Base class for orderable folderish AT Content Types"""

    __implements__ = (ATCTFolderMixin.__implements__,
                      OrderedBaseFolder.__implements__)

    security       = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Special case index_html"""
        request = REQUEST
        if request is None:
            request = getattr(self, 'REQUEST', None)
        if request and request.has_key('REQUEST_METHOD'):
            if request.maybe_webdav_client:
                method = request['REQUEST_METHOD']
                if method in ('PUT',):
                    # Very likely a WebDAV client trying to create something
                    return ReplaceableWrapper(NullResource(self, 'index_html'))
                elif method in ('GET', 'HEAD', 'POST'):
                    # Do nothing, let it go and acquire.
                    pass
                else:
                    raise AttributeError, 'index_html'
        # Acquire from parent
        _target = aq_parent(aq_inner(self)).aq_acquire('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

InitializeClass(ATCTOrderedFolder)


class ATCTBTreeFolder(ATCTFolderMixin, BaseBTreeFolder):
    """Base class for folderish AT Content Types using a BTree"""

    __implements__ = ATCTFolderMixin.__implements__, \
                     BaseBTreeFolder.__implements__

    security       = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """
        BTree folders don't store objects as attributes, the
        implementation of index_html method in PloneFolder assumes
        this and by virtue of being invoked looked in the parent
        container. We override here to check the BTree data structs,
        and then perform the same lookup as BasePloneFolder if we
        don't find it.
        """
        _target = self.get('index_html')
        if _target is not None:
            return _target
        _target = aq_parent(aq_inner(self)).aq_acquire('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

InitializeClass(ATCTBTreeFolder)


__all__ = ('ATCTContent', 'ATCTFolder', 'ATCTOrderedFolder',
           'ATCTBTreeFolder' )
