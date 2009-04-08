# -*- coding: utf-8 -*-
## CMFPlacefulWorkflow
## Copyright (C)2006 Ingeniweb

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
CMFPlacefulWorkflow.interfaces package
"""
__version__ = "$Revision: 39673 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: __init__.py 39673 2007-03-24 00:12:36Z encolpe $
__docformat__ = 'restructuredtext'

from Interface.bridge import createZope3Bridge

from portal_placeful_workflow import IPlacefulWorkflowTool, IWorkflowPolicyDefinition

# Zope 2 interfaces definition
import PlacefulWorkflow
import WorkflowPolicyDefinition
createZope3Bridge(IPlacefulWorkflowTool, PlacefulWorkflow, 'IPlacefulWorkflowTool')
createZope3Bridge(IWorkflowPolicyDefinition, WorkflowPolicyDefinition, 'IWorkflowPolicyDefinition')
