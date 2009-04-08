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
Patch for Plone workflow tool getChainFor method

This code stay here for historical reasons: ** DO NOT REMOVE IT **
"""
__version__ = "$Revision: 41399 $"
# $Source: /cvsroot/ingeniweb/CMFPlacefulWorkflow/patches/workflowtoolPatch.py,v $
# $Id: workflowtoolPatch.py 41399 2007-05-01 14:59:22Z encolpe $
__docformat__ = 'restructuredtext'

from Products.CMFPlone.WorkflowTool import WorkflowTool
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr

def getPlacefulChainFor(self, ob):
    """Monkey-patched by CMFPlacefulWorkflow to look for placeful workflow configurations.

    Goal: find a workflow chain in a policy

    Steps:
    1. ask the object if it contains a policy
    2. if it does, ask him for a chain
    3. if there's no chain for the type the we loop on the parent
    4. if the parent is the portal object or None we stop and we ask to portal_workflow

    Hint:
    If ob was a string, ask directly portal_worlfow\n\n
    """

    cbt = self._chains_by_type
    chain = None

    if type(ob) == type(''):
        # We are not in an object, then we can only get default from portal_workflow
        portal_type = ob
        if cbt is not None:
            chain = cbt.get(portal_type, None)
            # Note that if chain is not in cbt or has a value of None, we use a default chain.
        if chain is None:
            chain = self.getDefaultChainFor(ob)
            if chain is None:
                # CMFCore default
                return ()

    elif hasattr(aq_base(ob), '_getPortalTypeName'):
        portal_type = ob._getPortalTypeName()
    else:
        portal_type = None

    if portal_type is None or ob is None:
        return ()

    # Take some extra care when ob is a string
    is_policy_container = False
    objectids = []
    try:
        objectids = ob.objectIds()
    except AttributeError, TypeError:
        pass

    if WorkflowPolicyConfig_id in objectids:
        is_policy_container = True

    # Inspired by implementation in CPSWorkflowTool.py of CPSCore 3.9.0
    # Workflow needs to be determined by true containment not context
    # so we loop over the actual containers
    chain = None
    wfpolicyconfig = None
    current_ob = aq_inner(ob)
    # start_here is used to check 'In policy': We check it only in the first folder
    start_here = True
    portal = aq_base(getToolByName(self, 'portal_url').getPortalObject())
    while chain is None and current_ob is not None:
        if base_hasattr(current_ob, WorkflowPolicyConfig_id):
            wfpolicyconfig = getattr(current_ob, WorkflowPolicyConfig_id)
            chain = wfpolicyconfig.getPlacefulChainFor(portal_type, start_here=start_here)
            if chain is not None:
                return chain

        elif aq_base(current_ob) is portal:
            break
        start_here = False
        current_ob = aq_inner(aq_parent(current_ob))

    # Note that if chain is not in cbt or has a value of None, we use a default chain.
    if cbt is not None:
        chain = cbt.get(portal_type, None)
        # Note that if chain is not in cbt or has a value of
        # None, we use a default chain.
    if chain is None:
        chain = self.getDefaultChainFor(ob)
        if chain is None:
            # CMFCore default
            return ()

    return chain

# don't lose the docstrings
getPlacefulChainFor.__doc__ = '\n'.join((WorkflowTool.getChainFor.__doc__, getPlacefulChainFor.__doc__))
WorkflowTool.getChainFor = getPlacefulChainFor
