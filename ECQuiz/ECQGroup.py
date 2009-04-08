# -*- coding: iso-8859-1 -*-
#
# $Id: ECQGroup.py,v 1.1 2006/08/10 13:16:05 wfenske Exp $
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

import random

from AccessControl import ClassSecurityInfo
from Acquisition import *
from Products.Archetypes.utils import shasattr

from Products.Archetypes.public import Schema, BooleanField, StringField, \
     StringWidget, TextField, TextAreaWidget
#from Products.ATContentTypes.content.base import updateActions, updateAliases

from config import *
from permissions import *
from tools import *
from ECQAbstractGroup import ECQAbstractGroup

class ECQGroup(ECQAbstractGroup):
    """Groups several questions into a unit."""
    
    # See comments in 'ECQAbstractGroup' for an explanation
    # of the function of a schema, therein defined properties (fields) and 
    # internationalization of the widgets
    schema = ECQAbstractGroup.schema + Schema((
            StringField('title',
                required=False,
                searchable=True,
                default='',
                widget=StringWidget(
                    label_msgid='label_title',
                    description_msgid='title',
                    i18n_domain='plone'),
            ),
        ),)

    meta_type = 'ECQGroup'            # zope type name
    portal_type = meta_type           # plone type name
    archetype_name = 'Question Group' # friendly type name

    # Use the portal_factory for this type.  The portal_factory tool
    # allows users to initiate the creation objects in a such a way
    # that if they do not complete an edit form, no object is created
    # in the ZODB.
    #
    # This attribute is evaluated by the Extensions/Install.py script.
    use_portal_factory = True

    content_icon = 'ecq_group.png'

    typeDescription = "Using this form, you can create a question group."
    typeDescMsgId = 'description_edit_mcquestiongroup'
    
    security = ClassSecurityInfo()
    
    # The functions needed for ECQAbstractGroup,
    # 'getResults', 'setResults', 'isPublic' and
    # 'getEvaluationScripts' don't have to be implemented. They are
    # acquired from the group's parent

    security.declarePrivate('computeCandidatePoints')
    def computeCandidatePoints(self, result):
        """Return how many points the candidate got for the questions
        in this container.  If a custom evaluation script has been
        uploaded it will be invoked. Otherwise a default method will
        be used.
            
        @param candidateId The user ID of the candidate whose points
        you want to know."""
        customScript = self.getEvaluationScript(self.portal_type)
        questions = self.getQuestions(result)
        if not customScript: # default
            points = 0
            for question in questions:
                if not shasattr(question, 'getCandidatePoints'):
                    return None
                qPoints = question.getCandidatePoints(result)
                if not isNumeric(qPoints):
                    return None
                points += qPoints
            return points
        else: # custom
            return evalFunString(customScript, \
                                 CUSTOM_EVALUATION_FUNCTION_NAME, \
                                 [self, candidateId, questions])
        
        
# Register this type in Zope
registerATCTLogged(ECQGroup)
