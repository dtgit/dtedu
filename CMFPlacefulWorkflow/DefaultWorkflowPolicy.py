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
A simple workflow policy.
"""
__version__ = "$Revision: 44772 $"
# $Source: /cvsroot/ingeniweb/CMFPlacefulWorkflow/DefaultWorkflowPolicy.py,v $
# $Id: DefaultWorkflowPolicy.py 44772 2007-06-28 20:00:46Z rossp $
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from Globals import InitializeClass, PersistentMapping, DTMLFile
from Acquisition import aq_base

from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import addWorkflowPolicyFactory

from Products.CMFCore.permissions import ManagePortal

from Products.CMFPlacefulWorkflow.interfaces.portal_placeful_workflow \
        import IWorkflowPolicyDefinition
from Products.CMFPlacefulWorkflow.global_symbols import Log, LOG_DEBUG

from Globals import package_home
from os import path as os_path
_dtmldir = os_path.join( package_home( globals() ), 'dtml' )

from Products.CMFCore.utils import getToolByName

DEFAULT_CHAIN = '(Default)'
MARKER = '_MARKER'

class DefaultWorkflowPolicyDefinition (SimpleItemWithProperties):

    __implements__ = IWorkflowPolicyDefinition

    meta_type = 'WorkflowPolicy'
    id = 'default_workflow_policy'
    _isAWorkflowPolicy = 1

    _chains_by_type = None  # PersistentMapping
    _default_chain = None # Fallback to wf tool

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Workflows'
                       , 'action' : 'manage_selectWorkflows'
                       }
                     , { 'label' : 'Overview', 'action' : 'manage_overview' }
                     )

    #
    #   ZMI methods
    #
    security.declareProtected( ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainWorkflowPolicy', _dtmldir )

    def __init__(self, id):
        self.id = id
        self.title = ''
        self.description = ''

    _manage_defineLocalWorkflowPolicy = DTMLFile('defineLocalWorkflowPolicy', _dtmldir)

    security.declareProtected( ManagePortal, 'getId')
    def getId(self):
        """ Return the id
        """
        return self.id

    security.declareProtected( ManagePortal, 'getTitle')
    def getTitle(self):
        """ Return the title
        """
        title = getattr(self, 'title', '')
        return title

    security.declareProtected( ManagePortal, 'getDescription')
    def getDescription(self):
        """ Return the description
        """
        description = getattr(self, 'description', '')
        return description

    security.declareProtected( ManagePortal, 'setTitle')
    def setTitle(self, title):
        """ Set the title
        """
        self.title=title

    security.declareProtected( ManagePortal, 'setDescription')
    def setDescription(self, description):
        """ Set the description
        """
        self.description = description

    security.declareProtected( ManagePortal, 'manage_selectWorkflows')
    def manage_selectWorkflows(self, REQUEST, manage_tabs_message=None):
        """ Show a management screen for changing type to workflow connections.
        """
        cbt = self._chains_by_type
        ti = self._listTypeInfo()
        types_info = []
        for t in ti:
            id = t.getId()
            title = t.Title()
            if title == id:
                title = None
            if cbt is not None and cbt.has_key(id):
                chain = ', '.join(cbt[id])
            else:
                chain = DEFAULT_CHAIN
            types_info.append({'id': id,
                               'title': title,
                               'chain': chain})
        return self._manage_defineLocalWorkflowPolicy(
            REQUEST,
            default_chain=', '.join(self._default_chain or ()),
            types_info=types_info,
            management_view='Workflows',
            manage_tabs_message=manage_tabs_message)


    security.declareProtected( ManagePortal, 'manage_changeWorkflows')
    def manage_changeWorkflows(self, title, description, default_chain, props=None, REQUEST=None):
        """ Changes which workflows apply to objects of which type.
        """
        self.title = title
        self.description = description

        wf_tool = getToolByName(self, 'portal_workflow')

        if props is None:
            props = REQUEST
        cbt = self._chains_by_type
        if cbt is None:
            self._chains_by_type = cbt = PersistentMapping()
        ti = self._listTypeInfo()
        # Set up the chains by type.
        for t in ti:
            id = t.getId()
            field_name = 'chain_%s' % id
            chain = props.get(field_name, DEFAULT_CHAIN).strip()
            self.setChain(id, chain)

        # Set up the default chain.
        self.setDefaultChain(default_chain)
        if REQUEST is not None:
            return self.manage_selectWorkflows(REQUEST,
                            manage_tabs_message='Changed.')
    manage_changeWorkflows = postonly(manage_changeWorkflows)

    security.declareProtected( ManagePortal, 'setChainForPortalTypes')
    def setChainForPortalTypes(self, pt_names, chain, REQUEST=None):
        """ Set a chain for portal types.
        """
        for portal_type in pt_names:
            self.setChain(portal_type, chain)
    setChainForPortalTypes = postonly(setChainForPortalTypes)

    security.declareProtected( ManagePortal, 'getChainFor')
    def getChainFor(self, ob, managescreen=False):
        """Returns the chain that applies to the object.

        If chain doesn't exist we return None to get a fallback from portal_workflow.
        We never return emtpy tuple that is good value for a chain.
        """

        cbt = self._chains_by_type
        if type(ob) == type(''):
            pt = ob
        elif hasattr(aq_base(ob), '_getPortalTypeName'):
            pt = ob._getPortalTypeName()
        else:
            pt = None

        if pt is None:
            return None

        chain = None
        if cbt is not None:
            chain = cbt.get(pt, MARKER)

        # Backwards compatibility: before chain was a string, not a list
        if chain is not MARKER and type(chain) == type(''):
            chain = map( lambda x: x.strip(), chain.split(',') )

        Log(LOG_DEBUG, 'Chain founded in policy', chain)
        if chain is MARKER or chain is None:
            return None
        elif len(chain) == 1 and chain[0] == DEFAULT_CHAIN:
            default = self.getDefaultChain(ob)
            if default:
                if managescreen:
                    return chain[0]
                else:
                    return default
            else:
                return None

        return chain

    security.declareProtected( ManagePortal, 'setDefaultChain')
    def setDefaultChain(self, default_chain, REQUEST=None):

        """ Sets the default chain for this tool. """
        wftool = getToolByName(self, 'portal_workflow')

        if type(default_chain) is type(''):
            default_chain = map( lambda x: x.strip(), default_chain.split(',') )
        ids = []
        for wf_id in default_chain:
            if wf_id:
                if not wftool.getWorkflowById(wf_id):
                    raise ValueError, ( "'%s' is not a workflow ID." % wf_id)
                ids.append(wf_id)

        self._default_chain = tuple(ids)
    setDefaultChain = postonly(setDefaultChain)

    security.declareProtected( ManagePortal, 'getDefaultChain')
    def getDefaultChain(self, ob):
        """ Returns the default chain."""
        if self._default_chain is None:
            wf_tool = getToolByName(self, 'portal_workflow')
            return wf_tool.getDefaultChainFor(ob)
        else:
            return self._default_chain

    security.declareProtected( ManagePortal, 'setChain')
    def setChain(self, portal_type, chain, REQUEST=None):
        """Set the chain for a portal type."""
        # Verify input data
        if portal_type not in [pt.id for pt in self._listTypeInfo()]:
            raise ValueError, ("'%s' is not a valid portal type." % portal_type)

        if type(chain) is type(''):
            chain = map( lambda x: x.strip(), chain.split(',') )

        wftool = getToolByName(self, 'portal_workflow')
        cbt = self._chains_by_type
        if cbt is None:
            self._chains_by_type = cbt = PersistentMapping()

        # if chain is None or default, we remove the entry
        if chain is None and cbt.has_key(portal_type):
            del cbt[portal_type]
        elif len(chain) == 1 and chain[0] == DEFAULT_CHAIN:
            cbt[portal_type] = chain
        else:
            for wf_id in chain:
                if wf_id != '' and not wftool.getWorkflowById(wf_id):
                    raise ValueError, ("'%s' is not a workflow ID." % wf_id)
            cbt[portal_type] = tuple(chain)
    setChain = postonly(setChain)

    security.declareProtected( ManagePortal, 'delChain')
    def delChain(self, portal_type, REQUEST=None):
        """Delete the chain for a portal type."""
        if self._chains_by_type.has_key(portal_type):
            del self._chains_by_type[portal_type]
    delChain = postonly(delChain)

    #
    #   Helper methods
    #
    security.declarePrivate( '_listTypeInfo' )
    def _listTypeInfo(self):

        """ List the portal types which are available.
        """
        pt = getToolByName(self, 'portal_types', None)
        if pt is None:
            return ()
        else:
            return pt.listTypeInfo()


InitializeClass(DefaultWorkflowPolicyDefinition)

addWorkflowPolicyFactory(DefaultWorkflowPolicyDefinition, title='Simple Policy')

