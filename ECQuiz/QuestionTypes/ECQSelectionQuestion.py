# -*- coding: iso-8859-1 -*-
#
# $Id: ECQSelectionQuestion.py,v 1.2 2006/08/14 11:39:14 wfenske Exp $
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

import random

from AccessControl import ClassSecurityInfo

from Acquisition import aq_base, aq_acquire, aq_inner, aq_parent

from Products.Archetypes.public import BaseFolder, BaseFolderSchema, \
BaseContent, BaseSchema, Schema, BooleanField, BooleanWidget, IntegerField, IntegerWidget, StringField, \
TextField, SelectionWidget, TextAreaWidget, StringWidget, RichWidget
#from Products.ATContentTypes.content.base import updateActions, updateAliases

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import *
from Products.ECQuiz.QuestionTypes.ECQBaseQuestion \
     import ECQBaseQuestion
from Products.ECQuiz.AnswerTypes.ECQSelectionAnswer \
     import ECQSelectionAnswer


class ECQSelectionQuestion(ECQBaseQuestion):
    """ A question that allows the candidate to select one or more of the 
        predefined answers contained in the question (ECQBaseQuestion is
        derived from 'BaseFolder').
    """

    schema = ECQBaseQuestion.schema + Schema((
            BooleanField('allowMultipleSelection',
                # If 'allowMultipleSelection' is True, this is a
                # multiple answer question, i.e. one where more than
                # one answer can be true. Otherwise it is a multiple
                # choice question, i.e. exactly only one answer is
                # correct.  The question_view template is designed to
                # support this. When 'allowMultipleSelection' is True,
                # radio buttons will be generated.  If not, check
                # boxes will be shown.  See also 'description'
                # property of the widget.
                accessor='isAllowMultipleSelection',
                default=1,
                searchable=False,
                widget=BooleanWidget(
                    label='Allow Multiple Selection',
                    label_msgid='allow_multiple_selection_label',
                    description='If the selection of multiple answers should be possible, mark this checkbox.',
                    description_msgid='allow_multiple_selection_tool_tip',
                    i18n_domain=I18N_DOMAIN),
                read_permission=PERMISSION_STUDENT,
            ),
            BooleanField("randomOrder", # See 'description' property
                                        # of the widget.
                accessor='isRandomOrder',
                required=False,
                default=1,
                read_permission=PERMISSION_INTERROGATOR,
                widget=BooleanWidget(
                    label='Randomize Answer Order',
                    label_msgid='randomize_answer_order_label',
                    description='Check this box if you want the answers '
                    'to this question to appear in a different, random '
                    'order for each candidate. Otherwise the '
                    'same order as in the &quot;contents&quot;-view will '
                    'be used.',
                    description_msgid='randomize_answer_order_tool_tip',
                    i18n_domain=I18N_DOMAIN),
                #read_permission=PERMISSION_STUDENT,
            ),
            IntegerField("numberOfRandomAnswers", # See 'description'
                                                  # property of the
                                                  # widget.
                default=-1,
                read_permission=PERMISSION_INTERROGATOR,
                widget=IntegerWidget(
                    label='Number of Random Answers',
                    label_msgid='number_of_random_answers_label',
                    description='The number of answers which are randomly '
                    'selected when a new quiz is generated for a candidate. '
                    '(This only works if &quot;Randomize Answer Order&quot; '
                    'is checked.)  A value &lt;= 0 means that all answers '
                    'will be used.',
                    description_msgid='number_of_random_answers_tool_tip',
                    i18n_domain=I18N_DOMAIN),
                #read_permission=PERMISSION_STUDENT,
            ),
        ),
    )
    
    # Use a custom page template for viewing.
    suppl_views = None
    default_view = immediate_view = 'ecq_selectionquestion_view'
    
#    aliases = updateAliases(ECQBaseQuestion, {
#        'view': default_view,
#        })
    
    allowed_content_types = (ECQSelectionAnswer.portal_type,)
    
    meta_type = 'ECQSelectionQuestion'    # zope type name
    portal_type = meta_type               # plone type name
    archetype_name = 'Selection Question' # friendly type name

    security = ClassSecurityInfo()
    
    security.declarePrivate('makeNewTest')
    def makeNewTest(self, candidateResult, suMode):
        """generate a new quiz"""
        allAnswers = self.contentValues()
        if self.isRandomOrder() and (not suMode):
            # use random order
            numRnd = min(len(allAnswers), self.getNumberOfRandomAnswers())
            if numRnd > 0:
                # Separate the correct answers
                correctAnswers = [a for a in allAnswers if a.isCorrect()]
                # Determine how many correct answers and how many
                # other answers to show
                maxNumCorrect = min(len(correctAnswers), numRnd)
                numCorrect    = random.randint(1, maxNumCorrect)
                numOther      = numRnd - numCorrect
                # Get the randomized correct answers
                rndCorrectAnswers = random.sample(correctAnswers, numCorrect)
                # Now choose numOther-many answers out of the ones
                # that are not in rndCorrectAnswers
                otherAnswers      = [a for a in allAnswers
                                     if a not in rndCorrectAnswers]
                rndOtherAnswers   = random.sample(otherAnswers,   numOther)
                
                suggestedAnswers = rndCorrectAnswers + rndOtherAnswers
            else:
                suggestedAnswers = allAnswers
            # Randomize the answers
            suggestedAnswers = random.sample(suggestedAnswers,
                                             len(suggestedAnswers))
        else:
            # Use the order in the "contents"-view
            suggestedAnswers = allAnswers
        suggestedAnswerIds = [answer.getId() for answer in suggestedAnswers]
        
        # Store the new suggested answer ids in the results object
        candidateResult.setSuggestedAnswer(self, suggestedAnswerIds)
    
    
    security.declareProtected(PERMISSION_STUDENT, 'getSuggestedAnswerIds')
    def getSuggestedAnswerIds(self, result):
        """Return a list with the IDs of the answer objects that were
        presented to the candidate.
        
        @param result The candidate's result object.
        """
        return result.getSuggestedAnswer(self)
    
    
    security.declareProtected(PERMISSION_STUDENT, 'getSuggestedAnswers')
    def getSuggestedAnswers(self, result):
        """Return a list with the actual answer objects that were
        presented to the candidate with ID candidateId.
        
        @param candidateId The user ID of the candidate.
        """
        allAnswers         = self.contentValues()
        suggestedAnswerIds = result.getSuggestedAnswer(self)
        retVal             = filterById(suggestedAnswerIds, allAnswers)
        return retVal


# Register this type in Zope
registerATCTLogged(ECQSelectionQuestion)
