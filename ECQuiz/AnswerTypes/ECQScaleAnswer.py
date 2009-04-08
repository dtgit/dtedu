# -*- coding: iso-8859-1 -*-
#
# $Id: ECQScaleAnswer.py,v 1.1 2006/10/19 19:54:17 wfenske Exp $
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

import re

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import BaseSchema, Schema, BooleanField, \
     StringField, TextField, SelectionWidget, TextAreaWidget, RichWidget, \
     BaseContent, FloatField
from Products.Archetypes.Widget import TypesWidget, IntegerWidget, \
     BooleanWidget, StringWidget, DecimalWidget

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import log, registerTypeLogged, \
     registerValidatorLogged
from Products.ECQuiz.AnswerTypes.ECQMCAnswer import ECQMCAnswer
from Products.ECQuiz.AnswerTypes.ECQSelectionAnswer import ECQSelectionAnswer
from Products.ECQuiz.InlineTextField import InlineTextField

from Products.validation.interfaces import ivalidator

class PercentageValidator:
    """A validator for percentages, ."""
    __implements__ = (ivalidator,)
    
    def __init__(self, name):
        self.name = name
        
    def __call__(self, value, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            decimalSeparator = \
                instance.translate(msgid = 'fraction_delimiter',
                                   domain = I18N_DOMAIN,
                                   default = '.')
            res = None
            match = re.match('^[0-9]+(\\'
                             + decimalSeparator
                             + r')?[0-9]*\s*%$', value)
            if match:
                return None
            else:
                return instance.translate(
                           msgid   = 'invalid_percentage',
                           domain  = I18N_DOMAIN,
                           default = 'Not a percentage: %s') % value
        else:
            return True

# Register this validator in Zope
registerValidatorLogged(PercentageValidator, 'percentage')

class ECQScaleAnswer(ECQMCAnswer):
    """An answer to a multiple-choice question that provides only some of the points."""
    
    schema = ECQMCAnswer.schema.copy() + Schema((
            FloatField(
                'score',
                accessor='getScorePrivate',
                mutator = 'setScore',
                edit_accessor = 'getScoreForEdit',
                default=0.0,
                searchable=False,
                validators=('percentage',),
                read_permission=PERMISSION_INTERROGATOR,
                widget=StringWidget(
                    label='Score',
                    label_msgid='partial_correct_label',
                    description='How many marks do you get for giving '
                    'this answer?  A higher value than the total for '
                    'this question will be reduced.',
                    description_msgid='partial_correct_tool_tip',
                    i18n_domain=I18N_DOMAIN,
                    size = 8,),
                ),),)
    
    # This type of question is always tutor-graded
    schema.delField('correct')
    
    # Use a custom page template for viewing.
    actions = (
        {
            'id': 'view',
            'action': 'string:${object_url}/ecq_scaleanswer_view',
        },
    )
    
    meta_type = 'ECQScaleAnswer'	# zope type name
    portal_type = meta_type		# plone type name
    archetype_name = 'Scale Answer'	# friendly type name

    # Use the portal_factory for this type.  The portal_factory tool
    # allows users to initiate the creation objects in a such a way
    # that if they do not complete an edit form, no object is created
    # in the ZODB.
    #
    # This attribute is evaluated by the Extensions/Install.py script.
    use_portal_factory = True

    security = ClassSecurityInfo()
    security.declareProtected(PERMISSION_STUDENT, 'getId')
    #security.declareProtected(PERMISSION_STUDENT, 'getAnswer')

    security.declareProtected(PERMISSION_GRADE, 'setScore')
    def setScore(self, input):
        """
        Mutator for the `score' field.  Allows the input of localized
        numbers.
        """
        #log("INPUT: %s (%s)\n" % (repr(input), repr(type(input))))
        if type(input) in (str, unicode):
            decimalSeparator = self.translate(msgid = 'fraction_delimiter',
                                              domain = I18N_DOMAIN,
                                              default = '.')
            # remove the `%' sign
            input = input[:-1]
            # de-localize the number
            score = input.replace(decimalSeparator, '.')
            score = float(score)
        else:
            score = input

        self.getField('score').set(self, score)

    security.declareProtected(PERMISSION_STUDENT, 'getScoreForEdit')
    def getScoreForEdit(self):
        # no docstring prevents publishing
        #
        # Edit accessor for the `score' field. Converts the stored score
        # into a localized representation.
        #
        # FIXME: check permissions: only return something to
        # candidates if we're in resultView
        
        number   = self.getScorePrivate()
        mctool   = getToolByName(self, 'ecq_tool')
        for_edit = mctool.localizeNumber('%f', number)
        for_edit = for_edit.rstrip('0')
        # make sure it doesn't end with the decimal separator
        if not for_edit[-1].isdigit():
            for_edit = for_edit + '0'
        # appedn the percent sign
        for_edit += '%'
        return for_edit
    
    security.declareProtected(PERMISSION_STUDENT, 'getScore')
    def getScore(self, *args, **kwargs):
        # no docstring prevents publishing
        #FIXME: check permissions: only return something if we're in resultView
        return self.getScorePrivate(*args, **kwargs)
    

# Register this type in Zope
registerTypeLogged(ECQScaleAnswer)
