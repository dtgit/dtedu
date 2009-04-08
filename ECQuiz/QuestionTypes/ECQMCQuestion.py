# -*- coding: iso-8859-1 -*-
#
# $Id: ECQMCQuestion.py,v 1.2 2006/08/14 11:39:14 wfenske Exp $
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
     BaseContent, BaseSchema, Schema, BooleanField, BooleanWidget, \
     IntegerField, IntegerWidget, StringField, TextField, SelectionWidget, \
     TextAreaWidget, StringWidget, RichWidget
#from Products.ATContentTypes.content.base import updateActions, updateAliases

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import *

from Products.ECQuiz.QuestionTypes.ECQSelectionQuestion \
     import ECQSelectionQuestion
from Products.ECQuiz.QuestionTypes.ECQPointsQuestion \
     import ECQPointsQuestion
from Products.ECQuiz.AnswerTypes.ECQMCAnswer import ECQMCAnswer


class ECQMCQuestion(ECQSelectionQuestion, ECQPointsQuestion):
    """A multiple-choice question."""

    """ This class represents a question in an ECQuiz.  The answers
    can be either right or wrong.  The candidate has to select which
    answer(s) he/she thinks is (are) correct.
    """

    schema = ECQSelectionQuestion.schema.copy() + ECQPointsQuestion.schema.copy()

    # Use a custom page template for viewing.
    suppl_views = None
    default_view = immediate_view = 'ecq_mcquestion_view'

#    for baseClass in (ECQSelectionQuestion,
#                      #ECQPointsQuestion,
#                      ):
#        aliases = updateAliases(baseClass, {
#            'view': default_view,
#            })

    # Only Answer objects may be put into this folder.
    allowed_content_types = (ECQMCAnswer.portal_type,)
    
    meta_type = 'ECQMCQuestion'    # zope type name
    portal_type = meta_type        # plone type name
    archetype_name = 'MC Question' # friendly type name

    # Use the portal_factory for this type.  The portal_factory tool
    # allows users to initiate the creation objects in a such a way
    # that if they do not complete an edit form, no object is created
    # in the ZODB.
    #
    # This attribute is evaluated by the Extensions/Install.py script.
    use_portal_factory = True

    security = ClassSecurityInfo()

    typeDescription = "Using this form, you can create a multiple-choice question."
    typeDescMsgId = 'description_edit_mcquestion'

    security.declarePrivate('getCorrectAnswerIds')
    def getCorrectAnswerIds(self, result):
        """ Return the IDs of the correct answers to this question that
            were presented to the candidate.

            @param result The result object of the candidate.
        """
        suggestedAnswerIds = self.getSuggestedAnswerIds(result)
        retVal = []
        for a in self.contentValues():
            aId = a.getId()
            if a.isCorrect() and (aId in suggestedAnswerIds):
                retVal.append(a.getId())
        return retVal
    
    
    security.declarePrivate('computeCandidatePoints')
    def computeCandidatePoints(self, result):
        """Return how many points the candidate got for this question.

        @param result The result object of the candidate.

        If a custom scoring script has been uploaded it will be
        invoked. Otherwise a default method will be used.
        """
        parent = getParent(self)
        
        # The IDs of the questions the candidate could have selected
        suggestedAnswerIds = self.getSuggestedAnswerIds(result)
        # The IDs of answers the candidate should have selected
        correctAnswerIds   = self.getCorrectAnswerIds(result)
        correctAnswerIds.sort()
        # The IDs of the answers the candidate did select
        givenAnswerIds     = result.getCandidateAnswer(self)
        
        #log("MC Question.getCorrectAnswerIds(): %s\n" % repr(retVal))
        
        customScript = parent.getEvaluationScript(self.portal_type)
        if customScript: # use custom script
            return evalFunString(customScript, CUSTOM_EVALUATION_FUNCTION_NAME,
                                 [self, result, givenAnswerIds])
        else: # default

            # The function selected in the edit tab of the quiz
            evalFun = parent.getScoringFunction()
            
            if evalFun == 'cruel': # A.K.A. 'all or nothing'
                if givenAnswerIds is None:
                    givenAnswerIds = []
                givenAnswerIds.sort()
                # Give all the points if everything was
                # correct. Otherwise, give no points.
                return [0, self.getPoints()][givenAnswerIds
                                             == correctAnswerIds]
            elif evalFun == 'guessing':
                minPoints = 0
                
                if givenAnswerIds is None:
                    return minPoints
                else:
                    numCorrectAnswers = len(correctAnswerIds)
                    numWrongAnswers   = len(suggestedAnswerIds) \
                                        - numCorrectAnswers
                    
                    points =   self.getPoints() * 1.0
                    plus   = 0
                    if numCorrectAnswers:
                        plus = points / numCorrectAnswers
                    minus  = 0
                    if numWrongAnswers:
                        minus = - points / numWrongAnswers 

                    # Loop over the given answers. Detract points for
                    # the wrong choices, add points for the correct
                    # ones.
                    score = 0.0
                    for givenAnswerId in givenAnswerIds:
                        score += [minus, plus][givenAnswerId
                                               in correctAnswerIds]
                    return max(score, minPoints)
            else:
                raise NotImplementedError(u"Scoring Function '%s'"
                                          % evalFun)


# Register this type in Zope
registerATCTLogged(ECQMCQuestion)
