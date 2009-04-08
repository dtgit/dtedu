## Validation Script (Python) "result_grade_validate"
##title=validates the form for grading results

#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# $Id: ecq_result_grade_validate.vpy,v 1.1 2006/08/10 13:16:17 wfenske Exp $
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

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

I18N_DOMAIN = context.i18n_domain

result = context
mctest = result.aq_inner.aq_parent
ecq_tool = context.ecq_tool
decimalSeparator = context.translate(msgid = 'fraction_delimiter',
                                     domain = I18N_DOMAIN,
                                     default = '.')

for group in [mctest] + mctest.getQuestionGroups():
    for question in group.getQuestions(result):
        if question.isTutorGraded():
            value = REQUEST.get(question.UID())[0].strip()
            if value:
                valueRepl = value.replace(decimalSeparator, '.')
                points = None
                try:
                    points = float(valueRepl)
                except ValueError:
                    msg = context.translate(
                        msgid   = 'invalid_score',
                        domain  = I18N_DOMAIN,
                        default = "Please enter a number or leave the "
                        "field empty.")
                    state.setError(question.UID(), msg)
                if points is not None:
                    maxPoints = question.getPoints()
                    if points > maxPoints:
                        maxStr = ecq_tool.localizeNumber('%.2f', maxPoints)
                        msg = context.translate(
                            msgid   = 'score_too_high',
                            domain  = I18N_DOMAIN,
                            default = 'This score is higher than the '
                            'maximum score for this question, %s.') % (maxStr,)
                        state.setError(question.UID(), msg)

if state.getErrors():
    state.set(status='failure',
              portal_status_message='Please correct the indicated errors.')
else:
    state.set(portal_status_message='Your changes have been saved.')

return state
