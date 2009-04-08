# -*- coding: iso-8859-1 -*-
#
# $Id: ECQBaseAnswer.py,v 1.1 2006/08/10 13:16:08 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import BaseSchema, Schema, BooleanField, \
     StringField, TextField, SelectionWidget, TextAreaWidget, RichWidget, \
     BaseContent
from Products.Archetypes.Widget import TypesWidget, IntegerWidget, \
     BooleanWidget, StringWidget

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import log, hideIdField, registerTypeLogged


class ECQBaseAnswer(BaseContent):
    """ A basic answer. The actual text has to be supplied by the candidate.
    """
    
    # This prevents the Questions from showing up as a portal content type
    global_allow = False

    localBaseSchema = BaseSchema.copy()
    
    schema = localBaseSchema + Schema((
        StringField(
        name='title',
        required=1,
        searchable=0,
        default='Answer',
        accessor='Title',
        widget=StringWidget(
            label_msgid='label_title',
            visible={'view' : 'invisible',
                     'edit' : 'invisible'},
            i18n_domain='plone',
            ),
        ),
        StringField(
        name='answerkey',
        required=1,
        searchable=0,
        default='',
        accessor='Answerkey',
        mode='r',
        widget=StringWidget(
            label_msgid='label_title',
            visible={'view' : 'visible'},
            i18n_domain=I18N_DOMAIN,
            ),
        ),
        ))

    # Use a custom page template for viewing.
    actions = (
        {
            'id': 'view',
            'action': 'string:${object_url}/ecq_baseanswer_view',
        },
    )
    
    meta_type = 'ECQBaseAnswer'    # zope type name
    portal_type = meta_type        # plone type name
    archetype_name = 'Base Answer' # friendly type name
    
    content_icon = 'ecq_answer.png'

    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    security = ClassSecurityInfo()
        
    
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        retVal = BaseContent.manage_afterAdd(self, item, container)
        self.syncResults('add')
        return retVal

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        retVal = BaseContent.manage_beforeDelete(self, item, container)
        self.syncResults('delete')
        return retVal

    def Answerkey(self):
        return self.letters[self.contentValues(filter =
                                               {'portal_type':
                                                self.portal_type}).index(self)]
    
    def Title(self):
        return self.archetype_name

# Register this type in Zope
registerTypeLogged(ECQBaseAnswer)
