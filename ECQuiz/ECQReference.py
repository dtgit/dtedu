# -*- coding: iso-8859-1 -*-
#
# $Id: ECQReference.py,v 1.2 2006/08/14 11:39:09 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema, BaseSchema, BaseContent, \
     ReferenceField, ObjectField, ReferenceWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget
from config import I18N_DOMAIN
from tools import getParent, log, registerTypeLogged


class ECQReference(BaseContent):
    """A reference to a question or a question group from another quiz."""
    schema = BaseSchema + Schema((
        ReferenceField('reference',
                       #allowed_types = (),
                       allowed_types_method = 'getAllowedRefTypes',
                       multiValued = False,
                       required = True,
                       relationship = 'alter_ego',
                       widget = ReferenceBrowserWidget(
                           description='Select a question or a question group from another quiz.',
                           description_msgid='reference_tool_tip',
                           i18n_domain=I18N_DOMAIN,
                           label='Reference',
                           label_msgid='reference_label',
                           allow_search = True,
                           show_indexes = False,
                           ),
                       ),
        ),)
    
    
    meta_type = 'ECQReference'       # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Reference'     # friendly type name

    # Use the portal_factory for this type.  The portal_factory tool
    # allows users to initiate the creation objects in a such a way
    # that if they do not complete an edit form, no object is created
    # in the ZODB.
    #
    # This attribute is evaluated by the Extensions/Install.py script.
    use_portal_factory = True

    # This type isn't directly allowed anywhere.
    global_allow = False

    content_icon = 'ecq_reference.png'
    
    security = ClassSecurityInfo()

    typeDescription = "Using this form, you can create a reference " \
                      "to a question or a question group from another quiz."
    typeDescMsgId = 'description_edit_mcreference'

    def getAllowedRefTypes(self, *args, **kwargs):
        parent = getParent(self)
        allowed = parent.allowed_content_types
        filtered = [t for t in allowed
                    if t not in (self.portal_type,
                                 'Folder', 'File', 'Image',)]
        return filtered
    
    
    # This attribute, along with '_notifyOfCopyTo' and
    # 'manage_afterAdd()', is a hack to allow us to keep the value of
    # the reference field after a 'ECQReference' object has
    # been copied.  After the copy operation, this attribute will hold
    # the old value of the 'reference' field and we can restore the
    # value in 'manage_afterAdd()'.
    copiedReference = None

    def _notifyOfCopyTo(self, container, op=0):
        """Retain the reference after copy, even though the Archetypes
        people really don't want us to."""
        #log("_notifyOfCopyTo %s\n" % str(self))
        refField = self.Schema().get('reference')
        refFieldValue = refField.get(self)
        self.copiedReference = refFieldValue
        return BaseContent._notifyOfCopyTo(self, container, op=op)
    
    def manage_afterAdd(self, item, container):
        """Retain the reference after copy, even though the Archetypes
        people really don't want us to."""
        # find out if we got copied
        isCopy = getattr(item, '_v_is_cp', False)
        # make a copy of the reference
        if isCopy:
            refField = self.Schema().get('reference')
            refFieldValue = refField.get(self) \
                            or self.copiedReference
                
        # let the super class do its thing
        retVal = BaseContent.manage_afterAdd(self, item, container)
        
        # put the reference back
        if isCopy and refFieldValue:
            refField.set(self, refFieldValue)

        # sync the result objects (totally unrelated to the previous
        # code)
        self.syncResults('add')
        return retVal


    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        retVal = BaseContent.manage_beforeDelete(self, item, container)
        self.syncResults('delete')
        return retVal


# Register this type in Zope
registerTypeLogged(ECQReference)
