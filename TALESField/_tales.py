##############################################################################
#
# TALESField - Field with TALES support for Archetypes
# Copyright (C) 2005 Sidnei da Silva, Daniel Nouri and contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
$Id: __init__.py,v 1.2 2005/02/26 17:56:10 sidnei Exp $
"""

from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
import Products.CMFCore.Expression as Expression

try:
    from Products.CMFCore.Expression import getExprContext
except ImportError:
    def getExprContext(context, object=None):
        request = getattr(context, 'REQUEST', None)
        if request:
            cache = request.get('_ec_cache', None)
            if cache is None:
                request['_ec_cache'] = cache = {}
            ec = cache.get( id(object), None )
        else:
            ec = None

        if ec is None:
            utool = getToolByName(context, 'portal_url')
            portal = utool.getPortalObject()
            if object is None or not hasattr(object, 'aq_base'):
                folder = portal
            else:
                folder = object
                # Search up the containment hierarchy until we find an
                # object that claims it's a folder.
                while folder is not None:
                    if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                        # found it.
                        break
                    else:
                        folder = aq_parent(aq_inner(folder))
            ec = Expression.createExprContext(folder, portal, object)
        if request:
            cache[ id(object) ] = ec
        return ec
