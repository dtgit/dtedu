# -*- coding: utf-8 -*-
# $Id: eca_workflow_scripts.py,v 1.1 2006/09/13 16:23:21 mxp Exp $
#
# Copyright (c) 2005 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# Workflow Scripts for: ecassignmentbox_workflow

__author__    = 'Michael Piotrowski <mxp@iws.cs.uni-magdeburg.de>'
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.1 $'

from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import log_exc
from Products.CMFCore.utils import getToolByName

def sendGradedEmail(self, state_change, **kw):
    state_change.object.sendGradingNotificationEmail()
