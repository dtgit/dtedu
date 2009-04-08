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
Import patches
"""
__version__ = "$Revision: 41400 $"
# $Source: /cvsroot/ingeniweb/CMFPlacefulWorkflow/patches/__init__.py,v $
# $Id: __init__.py 41400 2007-05-01 15:00:58Z encolpe $
__docformat__ = 'restructuredtext'


## Patch disabled in CMFPlone with version 3.0
## Make getChainFor method look for placeful workflow configuration
try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    from Products.CMFPlacefulWorkflow.global_symbols import Log, LOG_NOTICE
    Log(LOG_NOTICE, "Apply getChainFor monkey patch on WorkflowTool")
    import workflowtoolPatch
