# -*- coding: iso-8859-1 -*-
#
# $Id: ECQCorrectAnswer.py,v 1.2 2006/08/14 11:39:12 wfenske Exp $
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
from Products.ECQuiz.tools import log, registerTypeLogged
from Products.ECQuiz.AnswerTypes.ECQSelectionAnswer import ECQSelectionAnswer
from Products.ECQuiz.InlineTextField import InlineTextField

class ECQCorrectAnswer(ECQSelectionAnswer):
    """ An answer that can be either a right or wrong (in the context of
        a question that contains this answer).
    """

    schema = ECQSelectionAnswer.schema + Schema((
            InlineTextField('comment',
                accessor='getCommentPrivate',
                searchable=True,
                required=False,
                read_permission=PERMISSION_INTERROGATOR,
                allowable_content_types=('text/plain',
                    'text/structured',
                    'text/restructured',
                    'text/html',),
                default_output_type='text/html',
                widget=TextAreaWidget(
                    label='Comment',
                    label_msgid='answer_comment_label',
                    description='A comment on the answer. If the quiz '
                    'is set to "instant feedback", '
                    'the candidate will see this text in case his/her '
                    'answer was wrong.',
                    description_msgid='answer_comment_tool_tip',
                    i18n_domain=I18N_DOMAIN),
                validators=('isXML',),
            ),
            BooleanField('correct',
                accessor='isCorrectPrivate',
                default=0,
                searchable=False,
                read_permission=PERMISSION_INTERROGATOR,
                widget=BooleanWidget(
                    label='Correct',
                    label_msgid='correct_label',
                    description='The checkbox should be marked if this '
                    'is a correct answer.',
                    description_msgid='correct_tool_tip',
                    i18n_domain=I18N_DOMAIN),
            ),
        ),
    )
    
    # Use a custom page template for viewing.
    actions = (
        {
            'id': 'view',
            'action': 'string:${object_url}/ecq_correctanswer_view',
        },
    )
    
    meta_type = 'ECQCorrectAnswer'    # zope type name
    portal_type = meta_type           # plone type name
    archetype_name = 'Correct Answer' # friendly type name
    
    security = ClassSecurityInfo()
    security.declareProtected(PERMISSION_STUDENT, 'isCorrect')
    def isCorrect(self, *args, **kwargs):
        # no docstring prevents publishing
        #FIXME: check permssions: only return something if we're in resultView
        return self.isCorrectPrivate(*args, **kwargs)
        
    security.declareProtected(PERMISSION_STUDENT, 'getComment')
    def getComment(self, *args, **kwargs):
        # no docstring prevents publishing
        #FIXME: check permssions: only return something if we're in resultView
        return self.getCommentPrivate(*args, **kwargs)
    

# Register this type in Zope
registerTypeLogged(ECQCorrectAnswer)
