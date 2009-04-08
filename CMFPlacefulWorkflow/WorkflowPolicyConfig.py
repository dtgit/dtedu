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
Workflow Policy config
"""
__version__ = "$Revision: 44175 $"
# $Source: /cvsroot/ingeniweb/CMFPlacefulWorkflow/WorkflowPolicyConfig.py,v $
# $Id: WorkflowPolicyConfig.py 44175 2007-06-20 09:18:38Z encolpe $
__docformat__ = 'restructuredtext'

from Globals import DTMLFile, InitializeClass
from OFS.SimpleItem import SimpleItem

from AccessControl import ClassSecurityInfo

from PlacefulWorkflowTool import WorkflowPolicyConfig_id
from Products.CMFPlacefulWorkflow.global_symbols import Log, LOG_DEBUG

from Products.CMFCore.utils import getToolByName

manage_addWorkflowPolicyConfigForm=DTMLFile('dtml/addWorkflowPolicyConfig_form', globals())
def manage_addWorkflowPolicyConfig( self, REQUEST=None):
    ' add a Workflow Policy Configuratio into the system '
    workflow_policy_in = ''
    workflow_policy_below = ''
    if REQUEST:
        workflow_policy_in = REQUEST.get('workflow_policy_in', '')
        workflow_policy_below = REQUEST.get('workflow_policy_below', '')
    i = WorkflowPolicyConfig(workflow_policy_in, workflow_policy_below)   #create new workflow policy config
    self._setObject( WorkflowPolicyConfig_id,i )   #register it

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

class WorkflowPolicyConfig(SimpleItem):
    """Workflow policy configuration"""
    meta_type='Workflow Policy Configuration'
    manage=manage_main=DTMLFile('dtml/manageWorkflowPolicyConfig', globals())
    manage_main._setName('manage_main')
    index_html=None
    security = ClassSecurityInfo()

    manage_options=(
        (
        {'icon':'', 'label':'Edit',
         'action':'manage_main',},
        )
        +SimpleItem.manage_options
        )

    def __init__( self, workflow_policy_in='', workflow_policy_below='' ):
        """Initialize a new MailHost instance """
        self.id = ".wf_policy_conf"
        self.title = "Workflow policy configuration"
        self.setPolicyIn(workflow_policy_in)
        self.setPolicyBelow(workflow_policy_below)

    def manage_makeChanges(self, workflow_policy_in, workflow_policy_below):
        """ Store the policies """
        self.setPolicyIn(workflow_policy_in)
        self.setPolicyBelow(workflow_policy_below)

    def getPolicyInId(self):
        return self.workflow_policy_in

    def getPolicyBelowId(self):
        return  self.workflow_policy_below

    def getPolicyIn(self):
        pwt = getToolByName(self, 'portal_placeful_workflow')
        wfp_id = self.getPolicyInId()
        policy_in = pwt.getWorkflowPolicyById(wfp_id)
        return policy_in

    def getPolicyBelow(self):
        pwt = getToolByName(self, 'portal_placeful_workflow')
        wfp_id = self.getPolicyBelowId()
        policy_below = pwt.getWorkflowPolicyById(wfp_id)
        return policy_below

    def setPolicyIn(self, policy):
        if not type(policy) == type(''):
            raise ValueError, "Policy must be a string"
        self.workflow_policy_in = policy

    def setPolicyBelow(self, policy):
        if not type(policy) == type(''):
            raise ValueError, "Policy must be a string"
        self.workflow_policy_below = policy

    def getPlacefulChainFor(self, portal_type, start_here=False):
        """Get the chain for the given portal_type.

        Returns None if no placeful chain is found.
        Does _not_ acquire from parent configurations.

        Usecases:
        If the policy config is in the object that request the chain we cannot
        take the 'below' policy.
        In other case we test the 'below' policy first and, if there's no chain
        found, the 'in' policy.
        """
        workflow_tool = getToolByName(self, 'portal_placeful_workflow')
        Log(LOG_DEBUG, 'below policy id', self.getPolicyBelowId())
        Log(LOG_DEBUG, 'in policy id', self.getPolicyInId())

        chain = None
        policy = None
        if not start_here:
            policy = workflow_tool.getWorkflowPolicyById(self.getPolicyBelowId())
            # print "start here:", start_here, "type", portal_type, "policy", policy
            if policy != None:
                chain = policy.getChainFor(portal_type)

        policy = workflow_tool.getWorkflowPolicyById(self.getPolicyInId())
        # print "start here:", start_here, "type", portal_type, "policy", policy

        Log(LOG_DEBUG, "policy", repr(policy), policy != None)
        if chain == None and policy != None:
            chain = policy.getChainFor(portal_type)
            Log(LOG_DEBUG, "portal_type and chain", portal_type, chain)

        return chain

InitializeClass( WorkflowPolicyConfig )
