## Script (Python) "gradeResult"
##title=
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: ecq_result_grade_action.py,v 1.2 2007/07/04 01:09:26 wfenske Exp $
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

I18N_DOMAIN = context.i18n_domain

result = context
mctest = result.aq_inner.aq_parent
decimalSeparator = context.translate(msgid = 'fraction_delimiter',
                                     domain = I18N_DOMAIN,
                                     default = '.')
            
for group in [mctest] + mctest.getQuestionGroups():
    for question in group.getQuestions(result):
        if question.isTutorGraded():
            value = REQUEST.get(question.UID())[0].strip()
            if value:
                value = value.replace(decimalSeparator, '.')
                points = float(value)
                result.setTutorPoints(question, points)
            else:
                result.unsetTutorPoints(question)
            
msgid = 'Changes saved.'
msg = context.translate(
    msgid   = msgid,
    domain  = 'plone',
    default = msgid)

target = result.getActionInfo('object/grade')['url']
context.redirect('%s?portal_status_message=%s' % (target, msg))
