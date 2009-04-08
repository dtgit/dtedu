# -*- coding: iso-8859-1 -*-
#
# $Id: ECQResult.py,v 1.4 2006/10/19 19:15:01 wfenske Exp $
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


from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import Schema, BaseSchema, BaseContent, \
     ObjectField, IntegerField, StringField, DateTimeField, BooleanField
from Products.Archetypes.Widget import TypesWidget, StringWidget, \
     BooleanWidget
#from Products.ATContentTypes.content.base import updateActions, updateAliases
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin

from datetime import timedelta, datetime
from DateTime import DateTime

from config import *
from permissions import *
from tools import *
from ECQGroup import ECQGroup

class QuestionResult(object):
    def __init__(self, suggestedAnswer):
        self.NO_ANSWER = ['foo'] # an arbitrary object
        # Whatever the suggested answer(s) are
        self.suggestedAnswer = suggestedAnswer
        # What the candidate answered
        self.candidateAnswer = self.NO_ANSWER
        # A list of pairs: (starting time, finishing time)
        self.times           = []
        self.setCount        = 0
        # Points
        self.tutorPoints     = None
        self.cachedPoints    = None

    def getSuggestedAnswer(self):
        return self.suggestedAnswer
        
    def getCandidateAnswer(self):
        return self.candidateAnswer
        
    def setCandidateAnswer(self, new):
        if self.candidateAnswer != new:
            self.candidateAnswer = new
            self.setCount += 1

    def unsetCandidateAnswer(self):
        self.setCandidateAnswer(self.NO_ANSWER)

    def haveCandidateAnswer(self):
        return self.candidateAnswer is not self.NO_ANSWER

    def addTimeStart(self, timeStart):
        self.times.append((timeStart,))

    def addTimeFinish(self, timeFinish):
        assert(len(self.times) > 0)
        assert(len(self.times[-1]) == 1)
        
        timeStart = self.times[-1][0]
        self.times[-1] = (timeStart, timeFinish)

    def isWatchRunning(self):
        """Test whether the stop watch for the question is runnning."""
        # See if we have recorded any times and if so, if there is no
        # finish time for the last start time.
        return self.times and (len(self.times[-1]) == 1)

    def getTimeSpent(self):
        try:
            deltas = [(time[1] - time[0]) for time in self.times]
            total = reduce((lambda a, b: a+b), deltas, timedelta())
            return total
        except:
            return None

    def getSetCount(self):
        return self.setCount

    def getPoints(self):
        if self.tutorPoints is not None:
            return self.tutorPoints
        else:
            return self.cachedPoints


class ECQResult(ATCTContent, HistoryAwareMixin):
    """A quiz result."""

    """ This class contains all the candidate-specific information for
        an ECQuiz.  They are:

        questionResults:

          A dictionary that contains all the information concerning a
          single question, e. g. the suggested answer, the answer
          given by the candidate, the grade.

          The keys are the UIDs of the question.
                                   
        questionContainerIds:

          A list of the IDs of the 'ECQAbstractGroup'
          instances that the candidate saw.

        questionUIDs:

          A list of IDs of the questions that the candidate saw in
          their quiz.  Unfortunately 'questionResults.keys()' cannot
          be used since it does not preserve the order of the UIDs.
                                   
        timeStart:

          The time when the candidate first saw the quiz.
        
        timeFinish:

          The time when the candidate submitted their quiz.
    """    
    
    schema = ATContentTypeSchema.copy() + Schema((
        ObjectField('questionResults',
                    read_permission=PERMISSION_RESULT_READ,
                    default={},),
        ObjectField('possiblePointsCache',
                    read_permission=PERMISSION_RESULT_READ,
                    default={},),
        ObjectField('candidatePointsCache',
                    read_permission=PERMISSION_RESULT_READ,
                    default={},),
        ObjectField('questionContainerIds',
                    read_permission=PERMISSION_RESULT_READ,
                    default=[],),
        ObjectField('questionUIDs',
                    read_permission=PERMISSION_RESULT_READ,
                    default=[],),
        DateTimeField('timeStart',
                      read_permission=PERMISSION_RESULT_READ,),
        DateTimeField('timeFinish',
                      read_permission=PERMISSION_RESULT_READ,
                      default=None,),
        IntegerField('currentPageNum',
                     read_permission=PERMISSION_RESULT_READ,
                     write_permission=PERMISSION_RESULT_WRITE,
                     default=0,),
        ),)

    default_view = immediate_view = 'ecq_result_view'

#    aliases = updateAliases(ATCTContent, {
#        'view': default_view,
#        })

#    actions = updateActions(ATCTContent, (
#        {
#        'action':      'string:$object_url/ecq_result_grade',
#        'category':    'object',
#        'id':          'grade',
#        'name':        'Grade',
#        'permissions': (PERMISSION_GRADE,),
#        'condition':   'here/isGradable',
#        },
#        {
#        # Hack to remove the "Edit" tab
#        'action':      'string:$object_url/edit',
#        'category':    'object',
#        'id':          'edit',
#        'condition':   'python:0',
#        },
#        ))
    
    meta_type = 'ECQResult'   # zope type name
    portal_type = meta_type   # plone type name
    archetype_name = 'Result' # friendly type name

    # This type isn't directly allowed anywhere.
    global_allow = False
    # Don't list this type in the portal navigation.
    navigation_exclude = True

    content_icon = 'ecq_result.png'
    
    security = ClassSecurityInfo()

    
    security.declarePrivate('getQR')
    def getQR(self, caller, question, dontThrow=False):
        questionUID = question.UID()
        qrs = self.getQuestionResults()
        retVal = qrs.get(questionUID, None)
        if (retVal is not None) or dontThrow:
            return retVal
        else:
            txt = "%s() called for questionUID not in self.questionUIDs\n" \
                  "questionUID: %s\n" \
                  "self.questionUIDs: %s" \
                  % (caller, repr(questionUID), repr(self.getQuestionUIDs()))
            log(txt)
            raise Exception(txt)
    
    
    security.declarePrivate('storeQR')
    def storeQR(self, question, result):
        qrs = self.getQuestionResults()
        qrs[question.UID()] = result
        # Instead of saving "qrs" directly, save a copy of it,
        # "dict(qrs)".  If we don't do that, there is a chance that
        # Zope will return an old, cached value the next time
        # "self.getQuestionResults()" is called because it *thinks*
        # the cached dictionary is the same as the stored one because
        # the memory location didn't change.
        self.setQuestionResults(dict(qrs))

    security.declarePrivate('setSuggestedAnswer')
    def setSuggestedAnswer(self, question, suggestedAnswer):
        """ Saves the suggested answer values to a question the
            candidate was asked.
            
            @param suggestedAnswer The value or list of values
            of the answer suggested to the candidate.
                                        
            @param question The question that the answer belongs to.
                              
            @param questionContainerId The ID of the question
            container that contains the question.
        """
        # The list 'questionContainerIds' is neccessary because
        # 'self.questionResults.keys()' does not return the
        # questionUIDs in the order they were added.
        questionContainerId = getParent(question).getId()
        questionUID = question.UID()
        questionContainerIds = self.getQuestionContainerIds()
        if questionContainerId not in questionContainerIds:
            self.setQuestionContainerIds(questionContainerIds
                                         + [questionContainerId])
        questionUIDs = self.getQuestionUIDs()
        if questionUID not in questionUIDs:
            self.setQuestionUIDs(questionUIDs + [questionUID])
        qr = QuestionResult(suggestedAnswer)
        self.storeQR(question, qr)
        
        
    security.declareProtected(PERMISSION_RESULT_READ, 'getSuggestedAnswer')
    def getSuggestedAnswer(self, question):
        """ Returns the suggested answer values for a question the
            candidate was asked.  With the standard question and
            answer types this will be a list of IDs of answer objects.
        """
        qr = self.getQR("getAnswer", question)
        return qr.getSuggestedAnswer()
            

    security.declareProtected(PERMISSION_RESULT_READ, 'getCandidateAnswer')
    def getCandidateAnswer(self, question):
        """ Returns the candidate's answer to the question.  If this
        question was not part of their quiz, an exception will be
        raised.
        """
        qr =  self.getQR("getCandidateAnswer", question)
        return qr.getCandidateAnswer()
           
        
    security.declareProtected(PERMISSION_RESULT_WRITE, 'setCandidateAnswer')
    def setCandidateAnswer(self, question, answerValue):
        """ Saves the candidate's answer to a question.
            
            @param answerValue The value or list of values of the
            answer(s) the candidate gave. With the standard question
            and answer types this will be the ID (list of IDs) of the
            answer(s) the candidate selected.
        """
        qr = self.getQR("setCandidateAnswer", question)
        qr.setCandidateAnswer(answerValue)
        self.storeQR(question, qr)

    
    security.declareProtected(PERMISSION_RESULT_WRITE, 'unsetCandidateAnswer')
    def unsetCandidateAnswer(self, question):
        """ Removes the candidate's answer to a question.
            
            @param answerValue The value or list of values of the
            belongs to.
        """
        qr = self.getQR("unsetCandidateAnswer", question)
        qr.unsetCandidateAnswer()
        self.storeQR(question, qr)

    
    ## Points caching: start

    # Points for an individual question
    security.declareProtected(PERMISSION_RESULT_READ,
                              'getCachedQuestionPoints')
    def getCachedQuestionPoints(self, question):
        """
        """
        qr = self.getQR("getCachedQuestionPoints", question)
        return qr.cachedPoints
        
    security.declareProtected(PERMISSION_RESULT_WRITE,
                              'setCachedQuestionPoints')
    def setCachedQuestionPoints(self, question, value):
        """
        """
        qr = self.getQR("setCachedQuestionPoints", question)
        qr.cachedPoints = value
        self.storeQR(question, qr)

    # Tutor-assigned points for an individual question
    security.declareProtected(PERMISSION_GRADE, 'setTutorPoints')
    def getTutorPoints(self, question):
        """
        """
        qr = self.getQR("getTutorPoints", question)
        return qr.tutorPoints
        
    security.declareProtected(PERMISSION_GRADE, 'setTutorPoints')
    def setTutorPoints(self, question, value):
        """
        """
        qr = self.getQR("setTutorPoints", question)
        qr.tutorPoints = value
        self.storeQR(question, qr)

        # clear related cache info
        test = getParent(question)
        if test.portal_type == ECQGroup.portal_type:
            questionGroup = test
            test = getParent(questionGroup)
        else:
            questionGroup = None

        self.setCachedCandidatePoints(test, None)
        #log("%s: CachedCandidatePoints: %s\n" % (str(self), str(test)))
        if questionGroup:
            self.setCachedCandidatePoints(questionGroup, None)
            #log("%s: CachedCandidatePoints: %s\n" % (str(self),
            #                                         str(questionGroup)))
        #log("\n")
        
    security.declareProtected(PERMISSION_GRADE, 'unsetTutorPoints')
    def unsetTutorPoints(self, question):
        """
        """
        self.setTutorPoints(question, None) # this also clears any
                                            # related caches
        # Retract to "pending" because the result can't be "graded" if
        # some grades are missing
        userId = self.portal_membership.getAuthenticatedMember().getId()
        comment = "Retracted by %s: tutor grades were deleted" % userId
        self.tryWorkflowAction('retract_pending', ignoreErrors=True,
                               comment=comment)

    # Possible points for a question group
    security.declareProtected(PERMISSION_RESULT_READ,
                              'getCachedPossiblePoints')
    def getCachedPossiblePoints(self, questionGroup):
        """
        """
        cache = self.getPossiblePointsCache()
        return cache.get(questionGroup.UID(), None)
        
    security.declareProtected(PERMISSION_RESULT_WRITE,
                              'setCachedPossiblePoints')
    def setCachedPossiblePoints(self, questionGroup, value):
        """
        """
        cache = self.getPossiblePointsCache()
        cache[questionGroup.UID()] = value
        self.setPossiblePointsCache(dict(cache))

    # Achieved points for a question group
    security.declareProtected(PERMISSION_RESULT_READ,
                              'getCachedCandidatePoints')
    def getCachedCandidatePoints(self, questionGroup):
        """
        """
        cache = self.getCandidatePointsCache()
        return cache.get(questionGroup.UID(), None)
        
    security.declareProtected(PERMISSION_RESULT_WRITE,
                              'setCachedCandidatePoints')
    def setCachedCandidatePoints(self, questionGroup, value):
        """
        """
        cache = self.getCandidatePointsCache()
        cache[questionGroup.UID()] = value
        self.setCandidatePointsCache(dict(cache))
        
        
    # Delete all cached points
    security.declarePrivate('unsetAllCachedPoints')
    def unsetAllCachedPoints(self):
        # Delete cached points for the questions
        qrs = self.getQuestionResults()
        for qr in qrs.values():
            qr.cachedPoints = None
        self.setQuestionResults(dict(qrs))
        
        # Delete the caches for possible and candidate points in a
        # question group
        self.setPossiblePointsCache({})
        self.setCandidatePointsCache({})
        #log("%s: deleted all cached points\n" % (str(self)))

    # Clear all cached points related to the question [question],
    # i. e. clear cache for possible and achieved (candidate) points
    # for the question and the question group and the test that
    # contain this question
    security.declarePrivate('unsetCachedQuestionPoints')
    def unsetCachedQuestionPoints(self, question):
        """
        """
        if self.getQR("", question, dontThrow=True) is not None:
            test = getParent(question)
            if test.portal_type == ECQGroup.portal_type:
                questionGroup = test
                test = getParent(questionGroup)
            else:
                questionGroup = None

            self.setCachedQuestionPoints(question, None)
            #log("%s: CachedQuestionPoints: %s\n" % (str(self), str(question)))

            self.setCachedPossiblePoints(test, None)
            #log("%s: CachedPossiblePoints: %s\n" % (str(self), str(test)))
            self.setCachedCandidatePoints(test, None)
            #log("%s: CachedCandidatePoints: %s\n" % (str(self), str(test)))
            if questionGroup:
                self.setCachedPossiblePoints(questionGroup, None)
                #log("%s: CachedPossiblePoints: %s\n" % (str(self),
                #                                        str(questionGroup)))
                self.setCachedCandidatePoints(questionGroup, None)
                #log("%s: CachedCandidatePoints: %s\n" % (str(self),
                #                                         str(questionGroup)))
            #log("\n")

    ## Points caching: end

    
    security.declareProtected(PERMISSION_RESULT_READ, 'haveCandidateAnswer')
    def haveCandidateAnswer(self, question):
        qr = self.getQR("haveCandidateAnswer", question)
        return qr.haveCandidateAnswer()
    

    security.declareProtected(PERMISSION_RESULT_WRITE, 'startWatch')
    def startWatch(self, question):
        qr = self.getQR("startWatch", question)
        if not qr.isWatchRunning():
            qr.addTimeStart(datetime.now())
            #log("startWatch: %s\n" % str(question))
            self.storeQR(question, qr)
            makeTransactionUnundoable()
    
    
    security.declareProtected(PERMISSION_RESULT_WRITE, 'stopWatch')
    def stopWatch(self, question):
        qr = self.getQR("stopWatch", question)
        if qr.isWatchRunning():
            #log("stopWatch: %s\n" % str(question))
            qr.addTimeFinish(datetime.now())
            self.storeQR(question, qr)

    
    security.declareProtected(PERMISSION_RESULT_READ, 'isWatchRunning')
    def isWatchRunning(self, question):
        qr = self.getQR("isWatchRunning", question)
        return qr.isWatchRunning()

    
    security.declareProtected(PERMISSION_RESULT_READ, 'getTimeSpent')
    def getTimeSpent(self, question):
        """@return  A Python timedelta object."""
        qr = self.getQR("getTimeSpent", question)
        return qr.getTimeSpent()

    
    security.declareProtected(PERMISSION_RESULT_READ, 'getSetCount')
    def getSetCount(self, question):
        """@return The number of times the candidate changed his
        answer."""
        qr = self.getQR("getTimeSpent", question)
        return qr.getSetCount()

    
    security.declarePublic('getWorkflowState')
    def getWorkflowState(self):
        """Determine the Plone workflow state."""
        wtool = self.portal_workflow
        wf = wtool.getWorkflowsFor(self)[0]
        return wf.getInfoFor(self, 'review_state', '')


    security.declarePublic('hasState')
    def hasState(self, state):
        return self.getWorkflowState() == state


    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
        wtool = self.portal_workflow
        wf = wtool.getWorkflowsFor(self)[0]
        if wf.isActionSupported(self, action):
            if comment is None:
                userId = getSecurityManager().getUser().getId()
                comment = 'State changed by ' + userId
            wtool.doActionFor(self, action, comment=comment)
        elif not ignoreErrors:
            raise TypeError('Unsupported workflow action %s for object %s.'
                            % (repr(action), repr(self)))


    security.declarePublic('isGradable')
    def isGradable(self):
        mcTest=getParent(self)
        return mcTest.isTutorGraded(self) and \
               (self.getWorkflowState() in ("pending", "graded",))

    
    security.declareProtected(PERMISSION_RESULT_WRITE, 'submit')    
    def submit(self):
        self.setTimeFinish(DateTime())
        mcTest=getParent(self)
        results = mcTest.contentValues(filter =
                                       {'Creator'    : self.Creator(),
                                        'portal_type': self.portal_type,
                                        })
        for res in results:
            # determine workflow action: submit for self and supersede
            # for all the others
            if res == self:
                if mcTest.isTutorGraded(self):
                    action = 'submit_pending'
                else:
                    action = 'submit_graded'
                commentAction = 'Submitted'
            else:
                action = 'supersede'
                commentAction = 'Superseded'
            # execute the action
            comment='%s by %s' % (commentAction, self.Creator())
            res.tryWorkflowAction(action, ignoreErrors=True, comment=comment)


    security.declarePublic('isNewer')
    def isNewer(self, other):
        return self.getTimeStart() > other.getTimeStart()

    security.declarePublic('isMoreFinal')
    def isMoreFinal(self, other):
        STATES=['unsubmitted',
                'superseded',
                'pending',
                'graded',
                #'invalid',
                ]
        indexes = [STATES.index(o.getWorkflowState()) for o in self, other]
        return indexes[0] > indexes[1]

    
    security.declarePrivate('getViewerNames')
    def getViewerNames(self):
        """
        Get the names of the users and/or groups which have the local
        role ROLE_RESULT_VIEWER.  This allows reviewers to quickly
        check who may view an assignment.
        
        @return list of user and/or group names
        """
        principalIds = self.users_with_local_role(ROLE_RESULT_VIEWER)
        names = []
        
        for id in principalIds:
            if self.portal_groups.getGroupById(id):
                names.append(self.portal_groups.getGroupById(id).getGroupName())
            else:
                names.append(self.ecq_tool.getFullNameById(id))

        return names

    security.declarePublic('getIndicators')
    def getIndicators(self):
        """
        Returns a list of dictionaries which contain information necessary
        to display the indicator icons.
        """
        retVal = []

        user = self.portal_membership.getAuthenticatedMember()
        isOwner = user.has_role(['Owner', 'Reviewer', 'Manager'], self);
        isGrader = self.userIsGrader(user)

        viewers = self.getViewerNames()
        
        if viewers:
            if isOwner:
                retVal.append({'src':'ec_shared.png', 
                               'alt':'Released',
                               'alt_msgid':'label_released',
                               'title':'; '.join(viewers),
                               })
            elif isGrader:
                retVal.append({'src':'ec_shared.png', 
                               'alt':'Released',
                               'alt_msgid':'label_released',
                               'title':'These quiz results have been released for viewing.',
                               'title_msgid':'tooltip_released_icon',
                               })
        
#         if self.feedback:
#             feedback = str(self.feedback)
#             title = re.sub('[\r\n]+', ' ', feedback)[0:76]

#             retVal.append({'icon':'comment.png', 
#                            'alt':'Feedback',
#                            'alt_msgid':'label_feedback',
#                            'title':title,
#                            })

#         if isGrader and hasattr(self, 'remarks') and self.remarks:
#             remarks = str(self.remarks)
#             title = re.sub('[\r\n]+', ' ', remarks)[0:76]

#             retVal.append({'icon':'ecab_remarks.png', 
#                            'alt':'Remarks',
#                            'alt_msgid':'label_remarks',
#                            'title':title,
#                            })
        return retVal

    
    security.declarePublic('translateIndicators')
    def translateIndicators(self, indicators):
        # Translate [alt] and [title]
        for d in indicators:
            for k_msgid, k_msg in (('alt_msgid', 'alt',),
                                   ('title_msgid', 'title',)):
                msgid = d.get(k_msgid, None)
                if msgid is not None:
                    msg = d[k_msg]
                    d[k_msg] = self.translate(
                        msgid   = k_msg,
                        domain  = I18N_DOMAIN,
                        default = msg)
                    d.pop(k_msgid)
        
        return indicators
 

def createResult(context):
    """Create a new "ECQResult" object and initialize it."""
    retVal = createObject(context, ECQResult.portal_type)
    # for some obscure reason, this seems to be necessary
    retVal.unsetAllCachedPoints()
    now = DateTime()
    #setTitle(retVal, retVal.Creator() + ' ' + str(now))
    mctool = getToolByName(context, 'ecq_tool')
    name = mctool.getFullNameById(retVal.Creator())
    setTitle(retVal, name)
    retVal.setTimeStart(now)
    
    return retVal

# Register this type in Zope
registerATCTLogged(ECQResult)
