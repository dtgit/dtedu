# -*- coding: iso-8859-1 -*-
#
# $Id: ECQScaleQuestion.py,v 1.2 2007/06/27 17:40:37 mxp Exp $
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

from Products.Archetypes.public import Schema, StringField
from Products.Archetypes.Widget import SelectionWidget
from Products.Archetypes.utils import DisplayList
#from Products.ATContentTypes.content.base import updateActions, updateAliases

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import *
from Products.ECQuiz.QuestionTypes.ECQSelectionQuestion \
     import ECQSelectionQuestion
from Products.ECQuiz.QuestionTypes.ECQPointsQuestion \
     import ECQPointsQuestion
from Products.ECQuiz.AnswerTypes.ECQScaleAnswer import ECQScaleAnswer

class ECQScaleQuestion(ECQSelectionQuestion, ECQPointsQuestion):
    """A question that asks the candidate to give a rating for
    something.  'points', in this class, is the maximum rating. The
    answers are the possible ratings (e.g. 'very good', 'OK',
    'bad'). 'getCandidatePoints' returns which rating(s) has (have)
    been selected.
    """

    schema = ECQSelectionQuestion.schema.copy() + \
             ECQPointsQuestion.schema.copy() + Schema((
        StringField('choiceLayout', # the simpler name `layout' seems
                                    # to cause a conflict with Plone
                                    # or something
                    default='vertical',
                    enforceVocabulary=1,
                    vocabulary=DisplayList((
                        ('vertical', 'Vertical',
                         'layout_vertical_label'),
                        ('horizontal', 'Horizontal',
                         'layout_horizontal_label'),
                        )),
                    widget=SelectionWidget(
                        label='Layout',
                        label_msgid='layout_label',
                        description='Select &quot;vertical&quot; if you '
                        'want the choices to be listed from to top to '
                        'bottom. Select &quot;horizontal&quot; if you '
                        'want them to appear in a single row.',
                        description_msgid='layout_tool_tip',
                        i18n_domain=I18N_DOMAIN),
                    read_permission=PERMISSION_STUDENT,
                    write_permission=PERMISSION_GRADE,
                    ),
        ),)

    for i in range(4):
        schema.moveField('choiceLayout', -1)

    # Use a custom page template for viewing.
    suppl_views = None
    default_view = immediate_view = 'ecq_scalequestion_view'

#    for baseClass in (ECQSelectionQuestion,
                      #ECQPointsQuestion,
#                      ):
#        aliases = updateAliases(baseClass, {
#            'view': default_view,
#            })

    allowed_content_types = (ECQScaleAnswer.portal_type,)
    
    meta_type = 'ECQScaleQuestion'	# zope type name
    portal_type = meta_type		# plone type name
    archetype_name = 'Scale Question'	# friendly type name

    # This attribute is evaluated by the Extensions/Install.py script.
    use_portal_factory = True

    typeDescription = "A question which requires a selection of a point " \
                      "on a scale, e.g. for rating."
    typeDescMsgId = 'description_edit_scalequestion'

    security = ClassSecurityInfo()

    # Multiple selections don't make sense (at least for now)
    schema.delField('allowMultipleSelection')
    security.declarePublic('isAllowMultipleSelection')
    def isAllowMultipleSelection(self, *args, **kwargs):
        return False

    # This type of question is never tutor-graded
    schema.delField('tutorGraded')
    security.declarePublic('isTutorGraded')
    def isTutorGraded(self, *args, **kwargs):
        return False

    security.declarePrivate('computeCandidatePoints')
    def computeCandidatePoints(self, result):
        """Return how many points the user got for this question.

        @param result The result object of the candidate.

        If a custom evaluation script has been uploaded it will be
        invoked. Otherwise a default method will be used.
        """
        if not result.haveCandidateAnswer(self):
            return None
        
        parent = getParent(self)
        
        # The IDs of the questions the candidate could have selected
        suggestedAnswers = self.getSuggestedAnswers(result)
        # The IDs of the answers the candidate did select
        givenAnswerIds   = result.getCandidateAnswer(self)
        givenAnswers     = filterById(givenAnswerIds, suggestedAnswers)
        
        customScript = parent.getEvaluationScript(self.portal_type)
        if customScript: # use custom script
            return evalFunString(customScript, CUSTOM_EVALUATION_FUNCTION_NAME,
                                 [self, result, givenAnswerIds])
        else: # default
            # The function selected in the edit tab of the quiz
            maxPoints = self.getPointsPrivate()
            fact = maxPoints / 100.0
            score = 0
            for a in givenAnswers:
                score += fact * a.getScore()
            return score


# Register this type in Zope
registerATCTLogged(ECQScaleQuestion)
