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
""" Basic action list tool.

$Id: ActionsTool.py 76996 2007-06-24 00:18:49Z hannosch $
"""

from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Globals import InitializeClass
from OFS.ObjectManager import IFAwareObjectManager
from OFS.OrderedFolder import OrderedFolder
from zope.interface import implements

from ActionProviderBase import ActionProviderBase
from interfaces import IActionCategory
from interfaces import IActionProvider
from interfaces import IActionsTool
from interfaces.portal_actions import ActionProvider as z2IActionProvider
from interfaces.portal_actions import portal_actions as z2IActionsTool
from permissions import ManagePortal
from utils import _dtmldir
from utils import UniqueObject


class ActionsTool(UniqueObject, IFAwareObjectManager, OrderedFolder,
                  ActionProviderBase):

    """
        Weave together the various sources of "actions" which are apropos
        to the current user and context.
    """
    # XXX: this class violates the rules for tools/utilities:
    # ActionProviderBase depends implicitly on REQUEST

    implements(IActionsTool)
    __implements__ = (z2IActionsTool, OrderedFolder.__implements__,
                      ActionProviderBase.__implements__)

    id = 'portal_actions'
    meta_type = 'CMF Actions Tool'
    _product_interfaces = (IActionCategory,)
    action_providers = ('portal_types', 'portal_workflow', 'portal_actions')

    security = ClassSecurityInfo()

    manage_options = ( ( OrderedFolder.manage_options[0],
                         ActionProviderBase.manage_options[0],
                         {'label': 'Action Providers',
                          'action': 'manage_actionProviders'},
                         {'label': 'Overview',
                          'action': 'manage_overview'} ) +
                       OrderedFolder.manage_options[2:] )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainActionsTool', _dtmldir )
    manage_actionProviders = DTMLFile('manageActionProviders', _dtmldir)

    security.declareProtected(ManagePortal, 'manage_aproviders')
    def manage_aproviders(self
                        , apname=''
                        , chosen=()
                        , add_provider=0
                        , del_provider=0
                        , REQUEST=None):
        """
        Manage action providers through-the-web.
        """
        providers = list(self.listActionProviders())
        new_providers = []
        if add_provider:
            providers.append(apname)
        elif del_provider:
            for item in providers:
                if item not in chosen:
                    new_providers.append(item)
            providers = new_providers
        self.action_providers = tuple(providers)
        if REQUEST is not None:
            return self.manage_actionProviders(self , REQUEST
                          , manage_tabs_message='Providers changed.')

    security.declareProtected( ManagePortal, 'manage_editActionsForm' )
    def manage_editActionsForm( self, REQUEST, manage_tabs_message=None ):
        """ Show the 'Actions' management tab.
        """
        actions = [ ai.getMapping() for ai in self._actions ]

        # possible_permissions is in AccessControl.Role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form( self
                                 , REQUEST
                                 , actions=actions
                                 , possible_permissions=pp
                                 , management_view='Actions'
                                 , manage_tabs_message=manage_tabs_message
                                 )

    #
    #   ActionProvider interface
    #
    security.declarePrivate('listActions')
    def listActions(self, info=None, object=None):
        """ List all the actions defined by a provider.
        """
        actions = list(self._actions)
        for category in self.objectValues():
            actions.extend( category.listActions() )
        return tuple(actions)

    #
    #   Programmatically manipulate the list of action providers
    #
    security.declareProtected(ManagePortal, 'listActionProviders')
    def listActionProviders(self):
        """ List the ids of all Action Providers queried by this tool.
        """
        return self.action_providers

    security.declareProtected(ManagePortal, 'addActionProvider')
    def addActionProvider( self, provider_name ):
        """ Add an Action Provider id to the providers queried by this tool.
        """
        ap = list( self.action_providers )
        if hasattr( self, provider_name ) and provider_name not in ap:
            ap.append( provider_name )
            self.action_providers = tuple( ap )

    security.declareProtected(ManagePortal, 'deleteActionProvider')
    def deleteActionProvider( self, provider_name ):
        """ Delete an Action Provider id from providers queried by this tool.
        """
        ap = list( self.action_providers )
        if provider_name in ap:
            ap.remove( provider_name )
            self.action_providers = tuple( ap )

    #
    #   'portal_actions' interface methods
    #
    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None):
        """ List all actions available to the user.
        """
        actions = []

        # Include actions from specific tools.
        for provider_name in self.listActionProviders():
            provider = getattr(self, provider_name)
            if IActionProvider.providedBy(provider) or \
                    z2IActionProvider.isImplementedBy(provider):
                actions.extend( provider.listActionInfos(object=object) )

        # Include actions from object.
        if object is not None:
            if IActionProvider.providedBy(object) or \
                    z2IActionProvider.isImplementedBy(object):
                actions.extend( object.listActionInfos(object=object) )

        # Reorganize the actions by category.
        filtered_actions={'user':[],
                          'folder':[],
                          'object':[],
                          'global':[],
                          'workflow':[],
                          }

        for action in actions:
            catlist = filtered_actions.setdefault(action['category'], [])
            catlist.append(action)

        return filtered_actions

InitializeClass(ActionsTool)
