#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
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
""" Topic:

"""

__author__  = 'Alec Mitchell, Danny Bloemendaal'
__docformat__ = 'restructuredtext'
# __old_name__ = 'Products.ATContentTypes.types.criteria.ATPathCriterion'

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import Schema, DisplayList
from Products.Archetypes.public import BooleanField, StringField
from Products.Archetypes.public import BooleanWidget, SelectionWidget, StringWidget
from Products.Archetypes.Referenceable import Referenceable

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import PATH_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from Products.CMFCore.utils import getToolByName

ATRelativePathCriterionSchema = ATBaseCriterionSchema + Schema((
    StringField('relativePath',
                default='..',
                widget=StringWidget(label='Relative path', 
                                    label_msgid="label_relativepath_criteria_customrelativepath",
                                    description_msgid="help_relativepath_criteria_customrelativepath",
                                    i18n_domain="plone",
                                    description="Enter a relative path e.g.: <br /> '..' for the parent folder <br /> '../..' for the parent's parent <br />'../somefolder' for a sibling folder")),
    BooleanField('recurse',
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Recurse",
                default=False,
                widget=BooleanWidget(
                    label="Search Sub-Folders",
                    label_msgid="label_path_criteria_recurse",
                    description="",
                    description_msgid="help_path_criteria_recurse",
                    i18n_domain="plone"),
                ),
    ))

class ATRelativePathCriterion(ATBaseCriterion):
    """A path criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATRelativePathCriterionSchema
    meta_type      = 'ATRelativePathCriterion'
    archetype_name = 'Relative Path Criterion'
    shortDesc      = 'Location in site relative to the current location'

    def getNavTypes(self):
        ptool = self.plone_utils
        nav_types = ptool.typesToList()
        return nav_types

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []
        depth = (not self.Recurse() and 1) or -1
        relPath = self.getRelativePath()
        
        # sanitize a bit: you never know, with all those windoze users out there
        relPath = relPath.replace("\\","/") 

        # get the path to the portal object 
        portalPath = list(getToolByName(self, 'portal_url').getPortalObject().getPhysicalPath())
    
        if relPath[0]=='/':
            # someone didn't enter a relative path.
            # simply use that one, relative to the portal
            path = '/'.join(portalPath) + relPath
        elif relPath=='..' or relPath=='../':
            # do a shortcut
            path = '/'.join(self.aq_parent.aq_parent.getPhysicalPath())
        else:
            folders = relPath.split('/')

            # set the path to the collections path
            path = list(self.aq_parent.getPhysicalPath()) 
            
            # now construct an aboslute path based on the relative custom path
            # eat away from 'path' whenever we encounter a '..' in the relative path
            # apend all other elements other than ..
            for folder in folders:
                if folder == '..':
                    # chop off one level from path
                    if path == portalPath:
                        # can't chop off more
                        # just return this path and leave the loop
                        break
                    else:
                        path = path[:-1]
                elif folder == '.': 
                    # don't really need this but for being complete
                    # strictly speaking some user may use a . aswell
                    pass # do nothing
                else:
                    path.append(folder)
            path = '/'.join(path)

        if path is not '':
            result.append((self.Field(), {'query': path, 'depth': depth}))

        return tuple(result)


registerCriterion(ATRelativePathCriterion, PATH_INDICES)
