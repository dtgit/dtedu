## Script (Python) "submitTest"
##bind container=container
##bind context=context
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: ecq_quiz_submit.py,v 1.3 2007/07/04 01:09:26 wfenske Exp $
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

"""This script is called when a candidate submits his/her ECQuiz,
i.e. presses the 'Submit' button of the quiz form in ecq_quiz_view.pt.
"""

from AccessControl import getSecurityManager
from DateTime import DateTime

REQUEST     = container.REQUEST

I18N_DOMAIN = context.i18n_domain

user = getSecurityManager().getUser()
candidateId = user.getId()
suMode = context.userIsGrader(user)
# Check if "submit was pressed
gotSubmit = REQUEST.get('submit', False)
finished = gotSubmit
result = context.getCurrentResult()
ecq_tool = context.ecq_tool

# Check whether submission is allowed or not.
if context.mayResubmit():
    """Save the candidate's answers to all the questions he saw.
    """
    onePerPage    = context.isOnePerPage()
    onePerPageNav = context.isOnePerPageNav()
    # Get the number of the page that was displayed
    pageNum = result.getCurrentPageNum()
    # Calculate the number of pages there are
    questionsInTest    = context.getQuestions(result)
    numQuestionsInTest = len(questionsInTest)
    groups             = context.getQuestionGroups()
    numGroups          = len(groups)
            
    nullVal = ['I_DONT_KNOW']
    for group in [context] + groups:
        for question in group.getQuestions(result):
            # Check the value of the question if we're not in
            # 1-question-per-page-mode or if we are and the question
            # was displayed.
            check = False
            if (not onePerPage) or suMode:
                check = True
            elif pageNum < numQuestionsInTest:
                check = question == questionsInTest[pageNum]
            else:
                groupNum = pageNum-numQuestionsInTest
                check = (groupNum < numGroups) and (group == groups[groupNum])
            if check:
                name = candidateId + '_' + question.UID()
                candidateAnswer = REQUEST.get(name, nullVal)
                """The answer `nullVal' is a special case. An answer
                with that ID is generated for every multiple choice
                answer to allow the candidate to select nothing if
                he/she does not know which answer is correct but has
                already checked one of the radio buttons.
                """
                if candidateAnswer != nullVal:
                    result.setCandidateAnswer(question, candidateAnswer)
                else:
                    result.unsetCandidateAnswer(question)
        
            if result.isWatchRunning(question):
                result.stopWatch(question)
    
    if (not gotSubmit) and onePerPage:
        numPages = numQuestionsInTest + numGroups
        
        if onePerPageNav:
            haveNewPageNum = False
            # Check if one of the numbers was pressed
            for i in range(0, numPages):
                value = REQUEST.get('page_%d' % i, None)
                if value is not None:
                    pageNum = i
                    haveNewPageNum = True
                    break

            if not haveNewPageNum:
                # Else, see if "Next" or "Previous" was pressed.
                showPrevious = REQUEST.get('previous', False)
                showNext     = REQUEST.get('next',     False)
                if showPrevious:
                    pageNum -= 1
                elif showNext:
                    pageNum += 1
        
        else:
            # If navigation is not allowed, only check if 'next' was
            # pressed.
            if REQUEST.get('next', False):
                pageNum += 1
        
        # Save the new page number
        result.setCurrentPageNum(pageNum)
        # Find out if there's another page or if we're finished
        if pageNum < numPages:
            finished = False
            msg = None
    
    if finished:
        result.submit()
        msg = context.translate(msgid   = 'answers_saved',
                                domain  = I18N_DOMAIN,
                                default = 'Your answers have been saved.')
else:
    # Submission not allowed.
    msg = context.translate(msgid   = 'not_submit_again',
                            domain  = I18N_DOMAIN,
                            default = 'You may not submit the quiz again.')

# Disable "undo" by the candidate
ecq_tool.makeTransactionUnundoable()

# Redirect
if finished:
    target = result.getActionInfo('object/view')['url']
    # Set the 'portal_status_message' to 'msg' and set
    # 'has_just_submitted' to 'True'.  This prevents the 'You have
    # already taken this test.' message from being shown immediately
    # after submission.
    context.redirect('%s?portal_status_message=%s&has_just_submitted=True'
                     % (target, msg))
else:
    target = context.getActionInfo('object/view')['url']
    context.redirect(target)
