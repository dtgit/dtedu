# -*- coding: utf-8 -*-
## CMFPlacefulWorkflow
## Copyright (C)2005 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
PlacefulWorkflowTool main class
"""
__version__ = "$Revision: 44772 $"
# $Source: /cvsroot/ingeniweb/CMFPlacefulWorkflow/PlacefulWorkflowTool.py,v $
# $Id: PlacefulWorkflowTool.py 44772 2007-06-28 20:00:46Z rossp $
__docformat__ = 'restructuredtext'

from os import path as os_path

from Acquisition import aq_base
from AccessControl.requestmethod import postonly
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, package_home

from zope.interface import implements

from Products.CMFCore.utils import getToolByName, UniqueObject
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Products.CMFCore.utils import registerToolInterface


from interfaces import IPlacefulWorkflowTool
from interfaces.PlacefulWorkflow import IPlacefulWorkflowTool as z2IPlacefulWorkflowTool


_dtmldir = os_path.join( package_home( globals() ), 'dtml' )

WorkflowPolicyConfig_id  = ".wf_policy_config"

def addPlacefulWorkflowTool(self,REQUEST={}):
    """
    Factory method for the Placeful Workflow Tool
    """
    id='portal_placeful_workflow'
    pwt=PlacefulWorkflowTool()
    self._setObject(id, pwt, set_owner=0)
    getattr(self, id)._post_init()
    if REQUEST:
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_main')

class PlacefulWorkflowTool(UniqueObject, Folder, ActionProviderBase):
    """
    PlacefulWorkflow Tool
    """

    id = 'portal_placeful_workflow'
    meta_type = 'Placeful Workflow Tool'

    __implements__ = (z2IPlacefulWorkflowTool,)
    implements(IPlacefulWorkflowTool)

    _actions = []

    security = ClassSecurityInfo()


    manage_options=(
        ({
            'label': 'Content',
            'action': 'manage_main',
        },
         {
             'label' : 'Overview',
             'action' : 'manage_overview'
           },) +
        ActionProviderBase.manage_options +
        Folder.manage_options
        )

    def __init__(self):
        # Properties to be edited by site manager
        safeEditProperty(self, 'max_chain_length', 1, data_type='int')

    _manage_addWorkflowPolicyForm = DTMLFile('addWorkflowPolicy', _dtmldir)

    security.declareProtected( ManagePortal, 'manage_addWorkflowPolicyForm')
    def manage_addWorkflowPolicyForm(self, REQUEST):

        """ Form for adding workflow policies.
        """
        wfpt = []
        for key in _workflow_policy_factories.keys():
            wfpt.append(key)
        wfpt.sort()
        return self._manage_addWorkflowPolicyForm(REQUEST, workflow_policy_types=wfpt)

    security.declareProtected( ManagePortal, 'manage_addWorkflowPolicy')
    def manage_addWorkflowPolicy(self, id,
                                 workflow_policy_type='default_workflow_policy (Simple Policy)',
                                 duplicate_id='empty',
                                 RESPONSE=None,
				 REQUEST=None):
        """ Adds a workflow policies from the registered types.
        """
        if id in ('empty', 'portal_workflow'):
            raise ValueError, "'%s' is reserved. Please choose another id." % id

        factory = _workflow_policy_factories[workflow_policy_type]
        ob = factory(id)
        self._setObject(id, ob)

        if duplicate_id and duplicate_id != 'empty':
            types_tool = getToolByName(self, 'portal_types')
            new_wp = self.getWorkflowPolicyById(id)

            if duplicate_id == 'portal_workflow':
                wf_tool = getToolByName(self, 'portal_workflow')

                new_wp.setDefaultChain(wf_tool._default_chain)

                for ptype in types_tool.objectIds():
                    chain = wf_tool.getChainForPortalType(ptype, managescreen=True)
                    if chain:
                        new_wp.setChain(ptype, chain)

            else:
                orig_wp = self.getWorkflowPolicyById(duplicate_id)
                new_wp.setDefaultChain(orig_wp.getDefaultChain('Document'))

                for ptype in types_tool.objectIds():
                    chain = orig_wp.getChainFor(ptype, managescreen=True)
                    if chain:
                        new_wp.setChain(ptype, chain)

        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url() +
                              '/manage_main?management_view=Contents')
    manage_addWorkflowPolicy = postonly(manage_addWorkflowPolicy)

    def all_meta_types(self):
        return (
            {'name': 'WorkflowPolicy',
             'action': 'manage_addWorkflowPolicyForm',
             'permission': ManagePortal },)

    security.declareProtected( ManagePortal, 'getWorkflowPolicyById')
    def getWorkflowPolicyById(self, wfp_id):

        """ Retrieve a given workflow policy.
        """
        policy=None
        if wfp_id != None:
            wfp = getattr(self, wfp_id, None)
            if wfp !=None:
                if getattr(wfp, '_isAWorkflowPolicy', 0):
                    policy = wfp
        return policy

    security.declareProtected( ManagePortal, 'getWorkflowPolicyIds')
    def getWorkflowPolicies(self):
        """ Return the list of workflow policies.
        """
        wfps = []
        for obj_name, obj in self.objectItems():
            if getattr(obj, '_isAWorkflowPolicy', 0):
                wfps.append(obj)
        return tuple(wfps)

    security.declareProtected( ManagePortal, 'getWorkflowPolicyIds')
    def getWorkflowPolicyIds(self):

        """ Return the list of workflow policy ids.
        """
        wfp_ids = []

        for obj_name, obj in self.objectItems():
            if getattr(obj, '_isAWorkflowPolicy', 0):
                wfp_ids.append(obj_name)

        return tuple(wfp_ids)


    security.declareProtected( ManagePortal, 'getWorkflowPolicyConfig')
    def getWorkflowPolicyConfig(self, ob):
        local_config = None
        some_config = getattr(ob, WorkflowPolicyConfig_id, None)
        if some_config is not None:
            # Was it here or did we acquire?
             if hasattr(aq_base(ob), WorkflowPolicyConfig_id):
                 local_config = some_config
        return local_config

    def _post_init(self):
        """
        _post_init(self) => called from manage_add method, acquired within ZODB (__init__ is not)
        """
        pass

    #
    #   portal_workflow_policy implementation.
    #

    def getMaxChainLength(self):
        """Return the max workflow chain length"""
        max_chain_length = self.getProperty('max_chain_length')
        return max_chain_length

    def setMaxChainLength(self, max_chain_length):
        """Set the max workflow chain length"""
        safeEditProperty(self, 'max_chain_length', max_chain_length, data_type='int')

_workflow_policy_factories = {}

def _makeWorkflowPolicyFactoryKey(factory, id=None, title=None):
    # The factory should take one argument, id.
    if id is None:
        id = getattr(factory, 'id', '') or getattr(factory, 'meta_type', '')
    if title is None:
        title = getattr(factory, 'title', '')
    key = id
    if title:
        key = key + ' (%s)' % title
    return key

def addWorkflowPolicyFactory(factory, id=None, title=None):
    key = _makeWorkflowPolicyFactoryKey( factory, id, title )
    _workflow_policy_factories[key] = factory

def _removeWorkflowPolicyFactory( factory, id=None, title=None ):
    """ Make teardown in unitcase cleaner. """
    key = _makeWorkflowPolicyFactoryKey( factory, id, title )
    try:
        del _workflow_policy_factories[key]
    except KeyError:
        pass

InitializeClass(PlacefulWorkflowTool)
registerToolInterface('portal_placeful_workflow', IPlacefulWorkflowTool)
