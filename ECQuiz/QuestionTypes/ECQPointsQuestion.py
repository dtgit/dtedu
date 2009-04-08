# -*- coding: iso-8859-1 -*-
#
# $Id: ECQPointsQuestion.py,v 1.2 2006/08/14 11:39:14 wfenske Exp $
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

from Products.Archetypes.utils import shasattr
from Products.Archetypes.public import BaseFolder, BaseFolderSchema, \
     BaseContent, BaseSchema, Schema, BooleanField, BooleanWidget, \
     IntegerField, IntegerWidget, StringField, TextField, SelectionWidget, \
     TextAreaWidget, StringWidget, RichWidget
#from Products.ATContentTypes.content.base import updateActions, updateAliases

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import *
from Products.ECQuiz.QuestionTypes.ECQBaseQuestion import ECQBaseQuestion
from Products.ECQuiz.AnswerTypes.ECQCorrectAnswer import ECQCorrectAnswer

from Products.validation.interfaces import ivalidator


class ClearPointsCache:
    """A dummy validator that clears cached points for a question (and
    its question group and the quiz) from result objects."""
    __implements__ = (ivalidator,)
    
    def __init__(self, name):
        self.name = name
        
    def __call__(self, value, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            # [unsetCachedQuestionPoints] is found through acquisition magic
            instance.unsetCachedQuestionPoints(instance)
        return True

# Register this validator in Zope
registerValidatorLogged(ClearPointsCache, 'clearPointsCache')


class ECQPointsQuestion(ECQBaseQuestion):
    """ A question that can in some way be graded. The candidate's points 
        or the rating he/she gave, can be retieved via the 
        'getCandidatePoints()' method.
    """

    schema = ECQBaseQuestion.schema + Schema((
            IntegerField('points', # See 'description' property of the widget.
                accessor='getPointsPrivate',
                required=True,
                validators=('isPositiveInt', 'clearPointsCache',),
                read_permission=PERMISSION_INTERROGATOR,
                widget=IntegerWidget(
                    label='Points',
                    label_msgid='points_label',
                    description='The number of points assigned to this question.',
                    description_msgid='points_tool_tip',
                    i18n_domain=I18N_DOMAIN),
                #read_permission=PERMISSION_STUDENT,
            ),
            BooleanField('tutorGraded',
                accessor='isTutorGraded',
                default=False,
                #searchable=False,
                widget=BooleanWidget(
                    label='Tutor-Graded',
                    label_msgid='tutor_graded_label',
                    description='If answers to this question are graded manually, mark this checkbox.',
                    description_msgid='tutor_graded_tool_tip',
                    i18n_domain=I18N_DOMAIN),
                read_permission=PERMISSION_STUDENT,
                validators=('clearPointsCache',),
            ),
        ),
    )
    
    # Use a custom page template for viewing.
    suppl_views = None
    default_view = immediate_view = 'ecq_pointsquestion_view'
    
#    aliases = updateAliases(ECQBaseQuestion, {
#        'view': default_view,
#        })
    
    allowed_content_types = ECQBaseQuestion.allowed_content_types + \
                            (ECQCorrectAnswer.portal_type,)
    
    meta_type = 'ECQPointsQuestion'    # zope type name
    portal_type = meta_type            # plone type name
    archetype_name = 'Points Question' # friendly type name

    security = ClassSecurityInfo()

    security.declareProtected(PERMISSION_STUDENT, 'getPoints')
    def getPoints(self, *args, **kwargs):
        return self.getPointsPrivate(*args, **kwargs)


    security.declarePrivate('computeCandidatePoints')
    def computeCandidatePoints(self, result):
        """ Return how many points the candidate got for this question.

            @param result The result object of the candidate whose
            points you want to know.

            If a custom evaluation script has been uploaded it will be
            invoked. Otherwise a default method will be used.
        """
        parent = getParent(self)
        customScript = parent.getEvaluationScript(self.portal_type)
        answer = self.getCandidateAnswer(result)
        if not customScript: # default
            return None
        else: # use custom script
            return evalFunString(customScript, CUSTOM_EVALUATION_FUNCTION_NAME,
                                 [self, result, answer])

    
    def getCandidatePoints(self, result):
        if self.isTutorGraded():
            return result.getTutorPoints(self)
        else:
            # Check if we have a tutor-given or a cached value
            retVal = result.getCachedQuestionPoints(self)
            if retVal is None:
                retVal = self.computeCandidatePoints(result)
                result.setCachedQuestionPoints(self, retVal)
            return retVal


# Register this type in Zope
registerATCTLogged(ECQPointsQuestion)
