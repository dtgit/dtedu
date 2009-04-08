#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'

import logging
from cStringIO import StringIO
from zope.interface import implements

import AccessControl.Owned
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from ZODB.POSException import ConflictError

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal

from Products.ATContentTypes.interfaces import IImageContent
from Products.ATContentTypes.interfaces import IATCTTool as z2IATCTTool
from Products.ATContentTypes.interface import IATCTTool
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.config import WWW_DIR
from Products.ATContentTypes.tool.topic import ATTopicsTool

LOG = logging.getLogger('ATCT')

def log(message,summary='',severity=logging.DEBUG):
    LOG.log(severity, 'ATCT: %s \n%s', summary, message)

class ATCTTool(UniqueObject, SimpleItem, PropertyManager, ATTopicsTool):
    """ATContentTypes tool
    """
    security = ClassSecurityInfo()

    id = TOOLNAME
    meta_type= 'ATCT Tool'
    title = 'ATContentTypes Tool'

    __implements__ = (SimpleItem.__implements__, z2IATCTTool,
                      ATTopicsTool.__implements__)

    implements(IATCTTool)

    manage_options =  (
            {'label' : 'Overview', 'action' : 'manage_overview'},
            {'label' : 'Image scales', 'action' : 'manage_imageScales'}
        ) + PropertyManager.manage_options + \
            AccessControl.Owned.Owned.manage_options

    # properties

    _properties = PropertyManager._properties + (
        {'id' : 'image_types', 'type' : 'multiple selection',
         'mode' : 'w', 'select_variable' : 'listContentTypes'},
        {'id' : 'folder_types', 'type' : 'multiple selection',
         'mode' : 'w', 'select_variable' : 'listContentTypes'},
        {'id' : 'album_batch_size', 'type' : 'int', 'mode' : 'w'},
        {'id' : 'album_image_scale', 'type' : 'string', 'mode' : 'w'},
        {'id' : 'single_image_scale', 'type' : 'string', 'mode' : 'w'},
        )

    # templates

    security.declareProtected(ManagePortal, 'manage_imageScales')
    manage_imageScales = PageTemplateFile('imageScales', WWW_DIR)

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('overview', WWW_DIR)

    def om_icons(self):
        icons = ({'path':'misc_/ATContentTypes/tool.gif',
                  'alt':self.meta_type,
                  'title':self.meta_type},)
        return icons

    # image scales

    security.declareProtected(ManagePortal, 'recreateImageScales')
    def recreateImageScales(self, portal_type=None):
        """Recreates AT Image scales (doesn't remove unused!)
        """
        if portal_type is None:
            portal_type = tuple(self.image_types)
        out = StringIO()
        print >> out, "Updating AT Image scales"
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(portal_type = portal_type,
                         portal_type_operator = 'or')
        for brain in brains:
            obj = brain.getObject()
            if obj is None:
                continue
            if not IImageContent.isImplementedBy(obj):
                continue
            try:
                state = obj._p_changed
            except (ConflictError, KeyboardInterrupt):
                raise
            except:
                state = 0

            field = obj.getField('image')
            if field is not None:
                print >> out, 'Updating %s' % obj.absolute_url(1)
                field.removeScales(obj)
                field.createScales(obj)

            if state is None:
                obj._p_deactivate()

        print >> out, "Updated AT Image scales"
        return out.getvalue()

    security.declareProtected(ManagePortal, 'listContentTypes')
    def listContentTypes(self):
        """List all content types. Used for image/folder_types property.
        """
        ttool = getToolByName(self, 'portal_types')
        return ttool.listContentTypes()

InitializeClass(ATCTTool)
registerToolInterface('portal_atct', IATCTTool)
