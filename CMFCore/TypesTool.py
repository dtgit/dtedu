##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Type registration tool.

$Id: TypesTool.py 77288 2007-07-02 07:29:27Z hannosch $
"""

import logging
from warnings import warn

import Products
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_get
from Globals import DTMLFile
from Globals import InitializeClass
from OFS.Folder import Folder
from OFS.ObjectManager import IFAwareObjectManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.interfaces import IFactory
from zope.i18nmessageid import Message
from zope.interface import implements

from ActionProviderBase import ActionProviderBase
from exceptions import AccessControl_Unauthorized
from exceptions import BadRequest
from exceptions import zExceptions_Unauthorized
from interfaces import ITypeInformation
from interfaces import ITypesTool
from interfaces.portal_types \
        import ContentTypeInformation as z2ITypeInformation
from interfaces.portal_types import portal_types as z2ITypesTool
from permissions import AccessContentsInformation
from permissions import ManagePortal
from permissions import View
from utils import _checkPermission
from utils import _dtmldir
from utils import _wwwdir
from utils import SimpleItemWithProperties
from utils import UniqueObject

logger = logging.getLogger('CMFCore.TypesTool')

_marker = []  # Create a new marker.


class TypeInformation(SimpleItemWithProperties, ActionProviderBase):

    """ Base class for information about a content type.
    """

    manage_options = ( SimpleItemWithProperties.manage_options[:1]
                     + ( {'label':'Aliases',
                          'action':'manage_aliases'}, )
                     + ActionProviderBase.manage_options
                     + SimpleItemWithProperties.manage_options[1:]
                     )

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_editProperties')
    security.declareProtected(ManagePortal, 'manage_changeProperties')
    security.declareProtected(ManagePortal, 'manage_propertiesForm')

    _basic_properties = (
        {'id':'title', 'type': 'string', 'mode':'w',
         'label':'Title'},
        {'id':'description', 'type': 'text', 'mode':'w',
         'label':'Description'},
        {'id':'i18n_domain', 'type': 'string', 'mode':'w',
         'label':'I18n Domain'},
        {'id':'content_icon', 'type': 'string', 'mode':'w',
         'label':'Icon'},
        {'id':'content_meta_type', 'type': 'string', 'mode':'w',
         'label':'Product meta type'},
        )

    _advanced_properties = (
        {'id':'immediate_view', 'type': 'string', 'mode':'w',
         'label':'Initial view name'},
        {'id':'global_allow', 'type': 'boolean', 'mode':'w',
         'label':'Implicitly addable?'},
        {'id':'filter_content_types', 'type': 'boolean', 'mode':'w',
         'label':'Filter content types?'},
        {'id':'allowed_content_types'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Allowed content types'
         , 'select_variable':'listContentTypes'
         },
        { 'id': 'allow_discussion', 'type': 'boolean', 'mode': 'w'
          , 'label': 'Allow Discussion?'
          },
        )

    title = ''
    description = ''
    i18n_domain = ''
    content_meta_type = ''
    content_icon = ''
    immediate_view = ''
    filter_content_types = True
    allowed_content_types = ()
    allow_discussion = False
    global_allow = True

    def __init__(self, id, **kw):

        self.id = id
        self._actions = ()
        self._aliases = {}

        if not kw:
            return

        kw = kw.copy()  # Get a modifiable dict.

        if (not kw.has_key('content_meta_type')
            and kw.has_key('meta_type')):
            kw['content_meta_type'] = kw['meta_type']

        if (not kw.has_key('content_icon')
            and kw.has_key('icon')):
            kw['content_icon'] = kw['icon']

        self.manage_changeProperties(**kw)

        actions = kw.get( 'actions', () )
        for action in actions:
            self.addAction(
                  id=action['id']
                , name=action['title']
                , action=action['action']
                , condition=action.get('condition')
                , permission=action.get( 'permissions', () )
                , category=action.get('category', 'object')
                , visible=action.get('visible', True)
                )

        self.setMethodAliases(kw.get('aliases', {}))

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_aliases')
    manage_aliases = PageTemplateFile( 'typeinfoAliases.zpt', _wwwdir )

    security.declareProtected(ManagePortal, 'manage_setMethodAliases')
    def manage_setMethodAliases(self, REQUEST):
        """ Config method aliases.
        """
        form = REQUEST.form
        aliases = {}
        for k, v in form['aliases'].items():
            v = v.strip()
            if v:
                aliases[k] = v

        _dict = {}
        for k, v in form['methods'].items():
            if aliases.has_key(k):
                _dict[ aliases[k] ] = v
        self.setMethodAliases(_dict)
        REQUEST.RESPONSE.redirect('%s/manage_aliases' % self.absolute_url())

    #
    #   Accessors
    #
    security.declareProtected(View, 'Title')
    def Title(self):
        """
            Return the "human readable" type name (note that it
            may not map exactly to the 'portal_type', e.g., for
            l10n/i18n or where a single content class is being
            used twice, under different names.
        """
        if self.title and self.i18n_domain:
            return Message(self.title, self.i18n_domain)
        else:
            return self.title or self.getId()

    security.declareProtected(View, 'Description')
    def Description(self):
        """
            Textual description of the class of objects (intended
            for display in a "constructor list").
        """
        if self.description and self.i18n_domain:
            return Message(self.description, self.i18n_domain)
        else:
            return self.description

    security.declareProtected(View, 'Metatype')
    def Metatype(self):
        """
            Returns the Zope 'meta_type' for this content object.
            May be used for building the list of portal content
            meta types.
        """
        return self.content_meta_type

    security.declareProtected(View, 'getIcon')
    def getIcon(self):
        """
            Returns the icon for this content object.
        """
        return self.content_icon

    security.declarePublic('allowType')
    def allowType( self, contentType ):
        """
            Can objects of 'contentType' be added to containers whose
            type object we are?
        """
        if not self.filter_content_types:
            ti = self.getTypeInfo( contentType )
            if ti is None or ti.globalAllow():
                return 1

        #If a type is enabled to filter and no content_types are allowed
        if not self.allowed_content_types:
            return 0

        if contentType in self.allowed_content_types:
            return 1

        return 0

    security.declarePublic('getId')
    def getId(self):
        return self.id

    security.declarePublic('allowDiscussion')
    def allowDiscussion( self ):
        """
            Can this type of object support discussion?
        """
        return self.allow_discussion

    security.declarePublic('globalAllow')
    def globalAllow(self):
        """
        Should this type be implicitly addable anywhere?
        """
        return self.global_allow

    security.declarePublic('listActions')
    def listActions(self, info=None, object=None):
        """ Return a sequence of the action info objects for this type.
        """
        return self._actions or ()

    security.declarePublic('constructInstance')
    def constructInstance(self, container, id, *args, **kw):
        """Build an instance of the type.

        Builds the instance in 'container', using 'id' as its id.
        Returns the object.
        """
        if not self.isConstructionAllowed(container):
            raise AccessControl_Unauthorized('Cannot create %s' % self.getId())

        ob = self._constructInstance(container, id, *args, **kw)

        return self._finishConstruction(ob)

    security.declarePrivate('_finishConstruction')
    def _finishConstruction(self, ob):
        """
            Finish the construction of a content object.
            Set its portal_type, insert it into the workflows.
        """
        if hasattr(ob, '_setPortalTypeName'):
            ob._setPortalTypeName(self.getId())

        if hasattr(aq_base(ob), 'notifyWorkflowCreated'):
            ob.notifyWorkflowCreated()

        ob.reindexObject()
        return ob

    security.declareProtected(ManagePortal, 'getMethodAliases')
    def getMethodAliases(self):
        """ Get method aliases dict.
        """
        aliases = self._aliases
        # for aliases created with CMF 1.5.0beta
        for key, method_id in aliases.items():
            if isinstance(method_id, tuple):
                aliases[key] = method_id[0]
                self._p_changed = True
        return aliases.copy()

    security.declareProtected(ManagePortal, 'setMethodAliases')
    def setMethodAliases(self, aliases):
        """ Set method aliases dict.
        """
        _dict = {}
        for k, v in aliases.items():
            v = v.strip()
            if v:
                _dict[ k.strip() ] = v
        if not getattr(self, '_aliases', None) == _dict:
            self._aliases = _dict
            return True
        else:
            return False

    security.declarePublic('queryMethodID')
    def queryMethodID(self, alias, default=None, context=None):
        """ Query method ID by alias.
        """
        aliases = self._aliases
        method_id = aliases.get(alias, default)
        # for aliases created with CMF 1.5.0beta
        if isinstance(method_id, tuple):
            method_id = method_id[0]
        return method_id

InitializeClass(TypeInformation)


class FactoryTypeInformation(TypeInformation):

    """ Portal content factory.
    """

    implements(ITypeInformation)
    __implements__ = z2ITypeInformation

    security = ClassSecurityInfo()

    _properties = (TypeInformation._basic_properties + (
        {'id':'product', 'type': 'string', 'mode':'w',
         'label':'Product name'},
        {'id':'factory', 'type': 'string', 'mode':'w',
         'label':'Product factory'},
        ) + TypeInformation._advanced_properties)

    product = ''
    factory = ''

    #
    #   Agent methods
    #
    def _getFactoryMethod(self, container, check_security=1):
        if not self.product or not self.factory:
            raise ValueError, ('Product factory for %s was undefined' %
                               self.getId())
        p = container.manage_addProduct[self.product]
        m = getattr(p, self.factory, None)
        if m is None:
            raise ValueError, ('Product factory for %s was invalid' %
                               self.getId())
        if not check_security:
            return m
        if getSecurityManager().validate(p, p, self.factory, m):
            return m
        raise AccessControl_Unauthorized( 'Cannot create %s' % self.getId() )

    def _queryFactoryMethod(self, container, default=None):

        if not self.product or not self.factory or container is None:
            return default

        # In case we aren't wrapped.
        dispatcher = getattr(container, 'manage_addProduct', None)

        if dispatcher is None:
            return default

        try:
            p = dispatcher[self.product]
        except AttributeError:
            logger.exception("_queryFactoryMethod raised an exception")
            return default

        m = getattr(p, self.factory, None)

        if m:
            try:
                # validate() can either raise Unauthorized or return 0 to
                # mean unauthorized.
                if getSecurityManager().validate(p, p, self.factory, m):
                    return m
            except zExceptions_Unauthorized:  # Catch *all* Unauths!
                pass

        return default

    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed(self, container):
        """
        a. Does the factory method exist?

        b. Is the factory method usable?

        c. Does the current user have the permission required in
        order to invoke the factory method?
        """
        if self.product:
            # oldstyle factory
            m = self._queryFactoryMethod(container)
            return (m is not None)

        elif container is not None:
            # newstyle factory
            m = queryUtility(IFactory, self.factory, None)
            if m is not None:
                for d in container.all_meta_types():
                    if d['name'] == self.content_meta_type:
                        sm = getSecurityManager()
                        return sm.checkPermission(d['permission'], container)

        return False

    security.declarePrivate('_constructInstance')
    def _constructInstance(self, container, id, *args, **kw):
        """Build a bare instance of the appropriate type.

        Does not do any security checks.

        Returns the object without calling _finishConstruction().
        """
        # XXX: this method violates the rules for tools/utilities:
        # it depends on self.REQUEST
        id = str(id)

        if self.product:
            # oldstyle factory
            m = self._getFactoryMethod(container, check_security=0)

            if getattr(aq_base(m), 'isDocTemp', 0):
                kw['id'] = id
                newid = m(m.aq_parent, self.REQUEST, *args, **kw)
            else:
                newid = m(id, *args, **kw)
            # allow factory to munge ID
            newid = newid or id

        else:
            # newstyle factory
            factory = getUtility(IFactory, self.factory)
            obj = factory(id, *args, **kw)
            rval = container._setObject(id, obj)
            newid = isinstance(rval, basestring) and rval or id

        return container._getOb(newid)

InitializeClass(FactoryTypeInformation)


class ScriptableTypeInformation(TypeInformation):

    """ Invokes a script rather than a factory to create the content.
    """

    implements(ITypeInformation)
    __implements__ = z2ITypeInformation

    security = ClassSecurityInfo()

    _properties = (TypeInformation._basic_properties + (
        {'id':'permission', 'type': 'string', 'mode':'w',
         'label':'Constructor permission'},
        {'id':'constructor_path', 'type': 'string', 'mode':'w',
         'label':'Constructor path'},
        ) + TypeInformation._advanced_properties)

    permission = ''
    constructor_path = ''

    #
    #   Agent methods
    #
    security.declarePublic('isConstructionAllowed')
    def isConstructionAllowed(self, container):
        """
        Does the current user have the permission required in
        order to construct an instance?
        """
        permission = self.permission
        if permission and not _checkPermission( permission, container ):
            return 0
        return 1

    security.declarePrivate('_constructInstance')
    def _constructInstance(self, container, id, *args, **kw):
        """Build a bare instance of the appropriate type.

        Does not do any security checks.

        Returns the object without calling _finishConstruction().
        """
        constructor = self.restrictedTraverse( self.constructor_path )

        # make sure ownership is explicit before switching the context
        if not hasattr( aq_base(constructor), '_owner' ):
            constructor._owner = aq_get(constructor, '_owner')
        #   Rewrap to get into container's context.
        constructor = aq_base(constructor).__of__( container )

        id = str(id)
        return constructor(container, id, *args, **kw)

InitializeClass(ScriptableTypeInformation)


allowedTypes = [
    'Script (Python)',
    'Python Method',
    'DTML Method',
    'External Method',
    ]


class TypesTool(UniqueObject, IFAwareObjectManager, Folder,
                ActionProviderBase):

    """ Provides a configurable registry of portal content types.
    """

    implements(ITypesTool)
    __implements__ = (z2ITypesTool, ActionProviderBase.__implements__)

    id = 'portal_types'
    meta_type = 'CMF Types Tool'
    _product_interfaces = (ITypeInformation,)

    security = ClassSecurityInfo()

    manage_options = ( Folder.manage_options[:1]
                     + ( {'label':'Aliases',
                          'action':'manage_aliases'}, )
                     + ActionProviderBase.manage_options
                     + ( {'label':'Overview',
                          'action':'manage_overview'}, )
                     + Folder.manage_options[1:]
                     )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainTypesTool', _dtmldir )

    security.declareProtected(ManagePortal, 'manage_aliases')
    manage_aliases = PageTemplateFile( 'typesAliases.zpt', _wwwdir )

    #
    #   ObjectManager methods
    #
    def all_meta_types(self, interfaces=None):
        # this is a workaround and should be removed again if allowedTypes
        # have an interface we can use in _product_interfaces
        all = TypesTool.inheritedAttribute('all_meta_types')(self)
        others = [ mt for mt in Products.meta_types
                   if mt['name'] in allowedTypes ]
        return tuple(all) + tuple(others)

    #
    #   other methods
    #
    security.declareProtected(ManagePortal, 'manage_addTypeInformation')
    def manage_addTypeInformation(self, add_meta_type, id=None,
                                  typeinfo_name=None, RESPONSE=None):
        """Create a TypeInformation in self.
        """
        # BBB: typeinfo_name is ignored
        if not id:
            raise BadRequest('An id is required.')
        for mt in Products.meta_types:
            if mt['name'] == add_meta_type:
                klass = mt['instance']
                break
        else:
            raise ValueError, (
                'Meta type %s is not a type class.' % add_meta_type)
        id = str(id)
        ob = klass(id)
        self._setObject(id, ob)
        if RESPONSE is not None:
            RESPONSE.redirect('%s/manage_main' % self.absolute_url())

    security.declareProtected(ManagePortal, 'manage_setTIMethodAliases')
    def manage_setTIMethodAliases(self, REQUEST):
        """ Config method aliases.
        """
        form = REQUEST.form
        aliases = {}
        for k, v in form['aliases'].items():
            v = v.strip()
            if v:
                aliases[k] = v

        for ti in self.listTypeInfo():
            _dict = {}
            for k, v in form[ ti.getId() ].items():
                if aliases.has_key(k):
                    _dict[ aliases[k] ] = v
            ti.setMethodAliases(_dict)
        REQUEST.RESPONSE.redirect('%s/manage_aliases' % self.absolute_url())

    security.declareProtected(AccessContentsInformation, 'getTypeInfo')
    def getTypeInfo( self, contentType ):
        """
            Return an instance which implements the
            TypeInformation interface, corresponding to
            the specified 'contentType'.  If contentType is actually
            an object, rather than a string, attempt to look up
            the appropriate type info using its portal_type.
        """
        if not isinstance(contentType, basestring):
            if hasattr(aq_base(contentType), 'getPortalTypeName'):
                contentType = contentType.getPortalTypeName()
                if contentType is None:
                    return None
            else:
                return None
        ob = getattr( self, contentType, None )
        if ITypeInformation.providedBy(ob):
            return ob
        if getattr(aq_base(ob), '_isTypeInformation', 0):
            # BBB
            warn("The '_isTypeInformation' marker attribute is deprecated, "
                 "and will be removed in CMF 2.3.  Please mark the instance "
                 "with the 'ITypeInformation' interface instead.",
                 DeprecationWarning, stacklevel=2)
            return ob
        else:
            return None

    security.declareProtected(AccessContentsInformation, 'listTypeInfo')
    def listTypeInfo( self, container=None ):
        """
            Return a sequence of instances which implement the
            TypeInformation interface, one for each content
            type registered in the portal.
        """
        rval = []
        for t in self.objectValues():
            # Filter out things that aren't TypeInformation and
            # types for which the user does not have adequate permission.
            if ITypeInformation.providedBy(t):
                rval.append(t)
            elif getattr(aq_base(t), '_isTypeInformation', 0):
                # BBB
                warn("The '_isTypeInformation' marker attribute is deprecated, "
                     "and will be removed in CMF 2.3.  Please mark the "
                     "instance with the 'ITypeInformation' interface instead.",
                     DeprecationWarning, stacklevel=2)
                rval.append(t)
        # Skip items with no ID:  old signal for "not ready"
        rval = [t for t in rval if t.getId()]
        # check we're allowed to access the type object
        if container is not None:
            rval = [t for t in rval if t.isConstructionAllowed(container)]
        return rval

    security.declareProtected(AccessContentsInformation, 'listContentTypes')
    def listContentTypes(self, container=None, by_metatype=0):
        """ List type info IDs.

        Passing 'by_metatype' is deprecated (type information may not
        correspond 1:1 to an underlying meta_type). This argument will be
        removed when CMFCore/dtml/catalogFind.dtml doesn't need it anymore.
        """
        typenames = {}
        for t in self.listTypeInfo( container ):

            if by_metatype:
                warn('TypeInformation.listContentTypes(by_metatype=1) is '
                     'deprecated.',
                     DeprecationWarning)
                name = t.Metatype()
            else:
                name = t.getId()

            if name:
                typenames[ name ] = None

        result = typenames.keys()
        result.sort()
        return result

    security.declarePublic('constructContent')
    def constructContent( self
                        , type_name
                        , container
                        , id
                        , RESPONSE=None
                        , *args
                        , **kw
                        ):
        """
            Build an instance of the appropriate content class in
            'container', using 'id'.
        """
        info = self.getTypeInfo( type_name )
        if info is None:
            raise ValueError('No such content type: %s' % type_name)

        ob = info.constructInstance(container, id, *args, **kw)

        if RESPONSE is not None:
            immediate_url = '%s/%s' % ( ob.absolute_url()
                                      , info.immediate_view )
            RESPONSE.redirect( immediate_url )

        return ob.getId()

    security.declarePrivate( 'listActions' )
    def listActions(self, info=None, object=None):
        """ List all the actions defined by a provider.
        """
        actions = list( self._actions )

        if object is None and info is not None:
            object = info.object
        if object is not None:
            type_info = self.getTypeInfo(object)
            if type_info is not None:
                actions.extend( type_info.listActions(info, object) )

        return actions

    security.declareProtected(ManagePortal, 'listMethodAliasKeys')
    def listMethodAliasKeys(self):
        """ List all defined method alias names.
        """
        _dict = {}
        for ti in self.listTypeInfo():
            aliases = ti.getMethodAliases()
            for k, v in aliases.items():
                _dict[k] = 1
        rval = _dict.keys()
        rval.sort()
        return rval

InitializeClass(TypesTool)
