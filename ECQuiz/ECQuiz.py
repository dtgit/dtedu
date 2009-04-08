# -*- coding: iso-8859-1 -*-
#
# $Id: ECQuiz.py,v 1.6 2007/04/27 14:21:30 mxp Exp $
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

import os, os.path
import re
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import *
from Products.Archetypes.utils import shasattr
from DateTime import DateTime
from zipfile import ZipFile
from Products.Archetypes.public import Schema, BooleanField, IntegerField, \
     ObjectField, StringField, Field
from Products.Archetypes.Widget import TypesWidget, BooleanWidget, \
     SelectionWidget
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
try: # Plone 2.0.5
    from Products.CMFPlone.PloneUtilities import localized_time
except: # Plone 2.1
    from Products.CMFPlone.utils import ulocalized_time as localized_time

from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.DataGridField.Column import Column

from config import *
from permissions import *
from ECQAbstractGroup \
     import ECQAbstractGroup
from QuestionTypes.ECQMCQuestion import ECQMCQuestion
from ECQGroup import ECQGroup
from ECQReference import ECQReference
from tools import *
from qti import importAssessmentItem, \
     importPackage, exportPackage
from ECQResult import ECQResult, createResult

#from Products.ATContentTypes.content.base import updateActions, updateAliases

from Statistics import Statistics

from Products.validation.interfaces import ivalidator
from Products.validation import validation
from Products.validation import ValidationChain
from Products.validation.exceptions import ValidatorError

import wikitool
#from wikitool import importQuiz,exportQuiz,convertQuiz,updateQuiz

class ClearWholePointsCache:
    """A dummy validator that clears any cached points from result objects."""
    __implements__ = (ivalidator,)
    
    def __init__(self, name):
        self.name = name
        
    def __call__(self, value, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            instance.unsetAllCachedPoints()
        return True

# Register this validator in Zope
registerValidatorLogged(ClearWholePointsCache, 'clearWholePointsCache')

class GradingScaleValidator:
    """A validator for grading scales."""
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
            non_empty = [v for v in value
                         if v['score'].strip() or v['grade'].strip()]
            
            for row in non_empty:
                grade = row['grade'].strip()
                if not grade:
                    label = instance.translate(
                        msgid   = 'grade',
                        domain  = I18N_DOMAIN,
                        default = "Grade")
                    res = instance.translate(
                        msgid   = 'error_required',
                        domain  = 'archetypes',
                        default = '%s is required, please correct.' % label,
                        mapping = {'name': label},)
                    break
                        
                score = row['score'].strip()
                if row is non_empty[-1]: # last score field should be empty
                    if len(score) != 0:
                        res = instance.translate(
                            msgid   = 'minimum_score_not_empty',
                            domain  = I18N_DOMAIN,
                            default = 'The minimum score column of the '
                            'last row must be empty.')
                else:
                    match = re.match('^[0-9]+(\\'
                                     + decimalSeparator
                                     + r')?[0-9]*\s*%?$', score)
                    if not match:
                        res = instance.translate(
                            msgid   = 'invalid_minimum_score',
                            domain  = I18N_DOMAIN,
                            default = 'Not a percentage or an absolute '
                            'value: %s') % score
                        break
            return res
        else:
            return True

class DataGridWidgetI18N(DataGridWidget):
    def getColumnLabels(self, field, whatever=None):
        """ Get user friendly names of all columns """

        names = []

        for id in field.getColumnIds():
            # Warn AT developer about his/her mistake
            if not self.columns.has_key(id):
                raise AttributeError, "DataGridWidget missing column definition for " + id + " in field " + field.getName()

            col = self.columns[id]
            names.append(col.getLabel(self))

        return names

# Register this validator in Zope
registerValidatorLogged(GradingScaleValidator, 'gradingScale')

class ColumnI18N(Column):
    def __init__(self, label, label_msgid=None, default=None):
        """ Create a column
        @param label User visible name
        @param label_msgid Message ID that is used to i18n the label
        """
        self.label = label
        self.default = default
        
        if label_msgid is None:
            label_msgid = label
        self.label_msgid = label_msgid

    def getLabel(self, widget):
        """ User friendly name for the column """
        return widget.translate(
                    msgid   = self.label_msgid,
                    domain  = widget.i18n_domain,
                    default = self.label)

class EvaluationScriptsWidget(TypesWidget):
    """ A custom widget for handling the 'evaluationScripts' 
        property of the ECQuiz.
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : 'evaluation_scripts_widget',
    })


class ECQuiz(ECQAbstractGroup):
    """An online quiz."""
    
    """This is the main class of the 'ECQuiz' Product.  An ECQuiz is
    basically a folder that contains questions and groups of
    questions, i.e. folders that contain questions."""
    
    # format: [file extension, column delimiter, row delimiter, 
    # start of text delimiter, end of text delimiter, escape char]
    RESULTS_EXPORT_FORMAT_TAB = ['tab', '\t', '\n', '"', '"', '"']
    RESULTS_EXPORT_FORMAT_CSV = ['csv', ';',  '\n', '"', '"', '"']
    RESULTS_EXPORT_FORMATS = [RESULTS_EXPORT_FORMAT_TAB, RESULTS_EXPORT_FORMAT_CSV]
    
    # See comments in 'ECQAbstractGroup' for an explanation
    # of the function of a schema, therein defined properties (fields) and 
    # internationalization of the widgets
    schema = ECQAbstractGroup.schema + Schema((
            BooleanField('instantFeedback',
                         # Instant feedback means that the candidate will see
                         # their results immediately after submitting their
                         # quiz.
                         required=False,
                         default=0,
                         accessor='isInstantFeedback',
                         widget=BooleanWidget(
                             label='Instant Feedback',
                             label_msgid='instant_feedback_label',
                             description='If you want to give the candidates '
                             'instant feedback check this box.',
                             description_msgid='instant_feedback_tool_tip',
                             i18n_domain=I18N_DOMAIN),
                         read_permission=PERMISSION_STUDENT,
            ),
            BooleanField('allowRepetition',
                         # See 'description' of the widget.
                         required=False,
                         default=0,
                         accessor='isAllowRepetition',
                         widget=BooleanWidget(
                             label='Allow Repetition',
                             label_msgid='allow_repetition_label',
                             description='If you want to allow repeated '
                             'submission of the quiz check this box.',
                             description_msgid='allow_repetition_tool_tip',
                             i18n_domain=I18N_DOMAIN),
                         read_permission=PERMISSION_STUDENT,
            ),
            BooleanField('onePerPage',
                         required=False,
                         default=False,
                         accessor='isOnePerPage',
                         widget=BooleanWidget(
                             label='One Question per Page',
                             label_msgid='one_per_page_label',
                             description='If checked, each question/'
                             'question group is displayed on a separate page.',
                             description_msgid='one_per_page_tool_tip',
                             i18n_domain=I18N_DOMAIN),
                         read_permission=PERMISSION_STUDENT,
            ),
            BooleanField('onePerPageNav',
                         required=False,
                         default=False,
                         accessor='isOnePerPageNav',
                         widget=BooleanWidget(
                             label='Allow Navigation',
                             label_msgid='one_per_page_nav_label',
                             description="Let's candidates answer questions "
                             "in an arbitrary order when the quiz is in "
                             "one-question-per-page-mode.",
                            description_msgid='one_per_page_nav_tool_tip',
                             i18n_domain=I18N_DOMAIN),
                         read_permission=PERMISSION_STUDENT,
            ),
#             ObjectField('evaluationScripts',
#                         # A dictionary for custom evaluation
#                         # scripts. It is possible to customize the
#                         # evaluation behavior of the ECQuiz
#                         # Product by uploading custom evaluation
#                         # scripts for 1) the ECQuiz, 2)
#                         # ECQGroup objects, 3) Question
#                         # objects. Otherwise a default evaluation
#                         # method will be used.  The keys of this
#                         # dictionary are the'portal_type' properties of 
#                         # those classes. The values will be the scripts.
#                         required=False,
#                         # Not sure what this does.
#                         multiValued=True,
#                         default={},
#                         mutator='setEvaluationScripts',
#                         widget=EvaluationScriptsWidget(
#                             types=CUSTOM_EVALUATION_TYPES),
#                         read_permission=PERMISSION_INTERROGATOR,
#             ),
            StringField('scoringFunction',
                        default='guessing',
                        enforceVocabulary=1,
                        vocabulary=DisplayList((
                            ('guessing', 'Guessing Correction',
                             'scoring_fun_guessing_correction_label'),
                            ('cruel', 'All or Nothing',
                             'scoring_fun_cruel_label'),
                            )),
                        widget=SelectionWidget(
                            label='Scoring Function',
                            label_msgid='scoring_fun_label',
                            description='The way the score for a question '
                            'is calculated.',
                            description_msgid='scoring_fun_tool_tip',
                            i18n_domain=I18N_DOMAIN),
                        read_permission=PERMISSION_STUDENT,
                        validators=('clearWholePointsCache',),
                        write_permission=PERMISSION_GRADE,
            ),
            DataGridField('gradingScale',
                          mutator = 'setGradingScale',
                          edit_accessor = 'getGradingScaleForEdit',
                          columns = ('grade', 'gradeinfo', 'score', ),
                          widget = DataGridWidgetI18N(
                              columns = {
                                  'grade' : ColumnI18N('Grade', 'grade'),
                                  'gradeinfo' : ColumnI18N('Grade info', 'gradeinfo'),
                                  'score' : ColumnI18N('Minimum Score',
                                                       'minscore'),
                                  },
                              label = "Grading Scale",
                              label_msgid = 'grading_scale_label',
                              description = 'Grades are issued according '
                              'to the following scale of point values.  The '
                              'minimum score can be specified as a '
                              'percentage or as an absolute value.  '
                              'Leave the minimum score column of the last row '
                              'empty; this grade will be used for all scores '
                              'which are not covered by one of the other '
                              'entries.',
                              description_msgid = 'grading_scale_tool_tip',
                              i18n_domain = I18N_DOMAIN,
                              ),
                          validators=('gradingScale',),
                          write_permission=PERMISSION_GRADE,
            ),
            ),)

    """ Inherit custom actions from 'ECQAbstractGroup' and redefine
        them and/or define some new ones. 
    """
    
    suppl_views = None
    default_view = immediate_view = 'ecq_quiz_view'

    typeDescription = "An online quiz."
    typeDescMsgId = 'description_edit_mctest'
    
#    aliases = updateAliases(ECQAbstractGroup, {
#        'view': default_view,
#        })

#    actions = updateActions(ECQAbstractGroup, (
#        {
#            'id'           : 'edit',
#            'action'       : 'string:$object_url/edit',
#            'category'     : 'object',
#            'permissions'  : (PERMISSION_GRADE,),
#        },
#        {
#            'id'           : 'import_export',
#            'name'         : 'Import/Export',
#            'action'       : 'string:${object_url}/ecq_quiz_import_export',
#            'permissions'  : (PERMISSION_INTERROGATOR,),
#        },
#        {
#            'id'           : 'wiki_edit',
#            'name'         : 'Quick edit',
#            'action'       : 'string:${object_url}/ecq_quiz_wiki_edit',
#            'permissions'  : (PERMISSION_INTERROGATOR,),
#        },
#        {
#            'id'           : 'results',
#            'name'         : 'Results',
#            'action'       : 'string:${object_url}/ecq_quiz_results',
#            'condition'    : 'python:not (not here.getResultsDict())',
#        },
#        {
#            'id'           : 'statistics',
#            'name'         : 'Statistics',
#            'action'       : 'string:${object_url}/ecq_quiz_statistics',
#            'permissions'  : (PERMISSION_GRADE,),
#            'condition'    : 'python:here.haveDetailedScores()',
#        },
#        ))
    
    
    meta_type = 'ECQuiz'       # zope type name
    portal_type = meta_type    # plone type name
    archetype_name = 'Quiz'    # friendly type name

    # Use the portal_factory for this type.  The portal_factory tool
    # allows users to initiate the creation objects in a such a way
    # that if they do not complete an edit form, no object is created
    # in the ZODB.
    #
    # This attribute is evaluated by the Extensions/Install.py script.
    use_portal_factory = True

    # Store the i18n domain in an attribute of the quiz so that we
    # don't have to hardcode it in scripts (Python) but can acquire it
    # instead.
    i18n_domain = I18N_DOMAIN
    
    # This type is directly allowed anywhere.
    global_allow = True
    # ECQuizs may only contain questions and groups of question.
    allowed_content_types = (ECQResult.portal_type,
                             ECQGroup.portal_type,
                             'Folder', 'File', 'Image') \
                             + ECQAbstractGroup.allowed_content_types
    
    """ A custom icon for ECQuizs. The icon is located in 
        the skins directory ('skins/ECQuiz') (It is possible to put
        it in another folder but the path must be known to Zope.). 
    """
    content_icon = 'ecq_quiz.png'
    
    security = ClassSecurityInfo()
    
    
    def __getattr__(self, key):
        """ This workaround method maps  read requests for the standard 
            Plone properties 'effective_date'  and 'expiration_date' to
            calls to  the Archetype  methods  'getEffectiveDate()'  and 
            'getExpirationDate()',  respectively. This way timed publi-
            shing/unpublishing works with ECQuizs, too.
              Consult  the Python  documentation  to  learn  more about
            '__getattr__()' methods.
        """
        if(key == 'effective_date'):
            return self.getEffectiveDate()
        elif(key == 'expiration_date'):
            return self.getExpirationDate()
        else:
            raise AttributeError("'%s' object has no attribute '%s'"
                                 %(repr(self), str(key)) )


    # Hack to allow graders to call edit_view
    security.declareProtected(PERMISSION_GRADE, 'processForm')
    def processForm(self, *args, **kwargs):
        return ECQAbstractGroup.processForm(self, *args, **kwargs)

    def validate(self, *args, **kwargs):
        """Validates the form data from the request.
        """
        errors = ECQAbstractGroup.validate(self, *args, **kwargs)
        # don't know where these come from, but they make the
        # validation fail for graders
        for k in ('immediatelyAddableTypes', 'locallyAllowedTypes',):
            try:
                errors.pop(k)
            except:
                pass
        return errors

    
    security.declarePrivate('getReferencedObjects')
    def getReferencedObjects(self):
        """Collect all objects referenced by a ECQReference
        object within this quiz (and its ECQGroups).
        """
        tmp = self.contentValues()
        all = list(tmp)
        for o in tmp:
            if o.portal_type == ECQGroup.portal_type:
                all.extend(o.contentValues())
        return [o.getReference() for o in all
                if o.portal_type == ECQReference.portal_type]
    

    security.declarePrivate('getTests')
    def getTests(self, referencedObjects):
        """Returns a list of the original ECQuizs that the
        objects in 'referencedObjects' come from.
        """
        ret = []
        for o in referencedObjects:
            # Call aq_parent() until we get the ECQuiz
            # that o came from.
            while True:                            
                o = aq_parent(o)
                if o:
                    if o.portal_type == ECQuiz.portal_type:
                        if not o in ret:
                            ret.append(o)
                        break
                else:
                    break
        return ret


    def __bobo_traverse__(self, REQUEST, name):
        """Through this function, images, files, etc. that were
        referenced by ECQReference objects in the quiz get
        found.

        It works by searching for the files in this quiz ('self') and
        in every quiz from which some question or question group was
        referenced.
        """
        try:
            if REQUEST.has_key('ACTUAL_URL'):
                referencedObjects = self.getReferencedObjects()
                tests = self.getTests(referencedObjects)
                #log("TESTS: %s\n" % str(tests))
                
                # we only need to do something if we got any new tests
                if tests:
                    # first, search in 'self', then try the others
                    tests = [self] + tests
                    # collect the values that need replacing
                    repl = {}
                    self_url = self.absolute_url()
                    for key in REQUEST.keys():
                        value = REQUEST[key]
                        if (type(value) in [str, unicode]) and \
                               (value.find(self_url) != -1):
                            repl[key] = value
                    
                    # try to get the requested object from one of the
                    # tests in 'tests'
                    for test in tests:
                        # rewrite the URL
                        for key, value in repl.items():
                            REQUEST[key] = value.replace(
                                self_url, test.absolute_url())
                        # try to get the object using the rewritten URL
                        try:
                            result = \
                                ECQAbstractGroup.__bobo_traverse__(
                                    test, REQUEST, name)
                        except Exception, e:
                            #log("Exception: %s\n" % str(e))
                            result = None
                        # return the object if we got anything
                        if result:
                            return result
        except Exception, e:
            #log("Exception: %s\n" % str(e))
            pass
            
        return ECQAbstractGroup.__bobo_traverse__(self, REQUEST, name)
    
    
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        ECQAbstractGroup.manage_afterAdd(self, item, container)
        # Add local role 'Manager' for the creator so that users can
        # create quizzes without having to be Manager
        creator = self.Creator()
        roles = list(self.get_local_roles_for_userid(creator))
        if 'Manager' not in roles:
            roles.append('Manager')

        # Create a user-defined role ROLE_RESULT_VIEWER.  This role
        # has the View permission in certain states (defined in
        # ECQResultWorkflow).  This can be used for model solutions:
        #
        # (1) Submit a result with the model solution.
        #
        # (2) Use the"Sharing" tab to assign the role
        #     ROLE_RESULT_VIEWER to the users or groups that should be
        #     allowed to view the assignment.
        #
        # Create a user-defined role ROLE_RESULT_GRADER.  The owner of
        # a quiz can use this role to delegate grading to other users.
        
        for role in [ROLE_RESULT_VIEWER, ROLE_RESULT_GRADER]:
            if role not in self.valid_roles():
                self.manage_defined_roles('Add Role',
                                          {'role': role})
            # Assign the local roles to the creator
            if role not in roles:
                roles.append(role)

        # Grant the GradeAssignments permission to the "ECAssignment
        # Grader" role.
        self.manage_permission(PERMISSION_GRADE,
                               roles=[ROLE_RESULT_GRADER,],
                               acquire=True)
        
        self.manage_setLocalRoles(creator, roles)
    
    
    security.declarePrivate('getResults')
    def getResults(self, candidateId=None):
        flt = {'portal_type' : ECQResult.portal_type}
        if candidateId is not None:
            flt['Creator'] = candidateId
        return self.contentValues(filter=flt)
    

    def getLatestSubmission(self, candidateId):
        retVal = None
        for item in self.getResults(candidateId):
            if ((not item.hasState('invalid')) and
                ((not retVal) or item.isMoreFinal(retVal))):
                retVal = item
        if not retVal:
            raise Exception('Found no submission for %s', repr(candidateId))
        return retVal


    def hasParticipated(self, candidateId):
        """ Find out if a quiz has been generated for candidate
        candidateId.
        """
        return not (not self.getResults(candidateId))
        
        
    def hasSubmitted(self, candidateId):
        """ Find out if a candidate has actually submitted/taken this
        quiz."""
        # log("ECQuiz.hasSubmitted():\n")
        for item in self.getResults(candidateId):
            if item.getWorkflowState() in ['pending', 'graded', 'superseded']:
                return True
        return False
        
    
    # security.declareProtected(PERMISSION_INTERROGATOR, 'getSubmitterIds')
    def getSubmitterIds(self):
        """Return the IDs of the candidates who have actually
        submitted/taken this quiz.
        """
        d = {}
        for item in self.getResults():
            if item.getWorkflowState() in ['pending', 'graded', 'superseded']:
                d[item.Creator()] = True
        return d.keys()

    
    # security.declareProtected(PERMISSION_INTERROGATOR, 'getParticipantIds')
    def getParticipantIds(self):
        """ Get the IDs of all the candidates for whom a quiz has been
        generated.
        """
        d = {}
        for r in self.getResults():
            d[r.Creator()] = True
        return d.keys()
    

    security.declareProtected(PERMISSION_STUDENT, 'mayResubmit')
    def mayResubmit(self):
        user = getSecurityManager().getUser()
        candidateId = user.getId()
        
        if self.userIsGrader(user):
            return True
        elif self.isPublic():
            if self.isAllowRepetition():
                return True
            else:
                return not self.hasSubmitted(candidateId)
        else:
            return False


    security.declarePublic('isTutorGraded')
    def isTutorGraded(self, result):
        for grp in [self] + self.getQuestionGroups():
            if ECQAbstractGroup.isTutorGraded(grp, result):
                return True
        return False
            

    security.declareProtected(PERMISSION_STUDENT, 'getCurrentResult')
    def getCurrentResult(self):
        user = getSecurityManager().getUser()
        candidateId = user.getId()
        
        for item in self.getResults(candidateId):
            if item.hasState('unsubmitted'):
                return item
        
        return None


    security.declarePublic('userIsGrader')
    def userIsGrader(self, user):
        mctool = getToolByName(self, 'ecq_tool')
        return mctool.userHasOneOfRoles(user,
                                        ('Manager', ROLE_RESULT_GRADER,),
                                        self)
    

    security.declarePublic('userIsManager')
    def userIsManager(self, user):
        mctool = getToolByName(self, 'ecq_tool')
        return mctool.userHasOneOfRoles(user, ('Manager',), self)
        

    security.declareProtected(PERMISSION_INTERROGATOR, 'maybeMakeNewTest')
    def maybeMakeNewTest(self):
        """If the candidate hasn't seen this quiz yet, generate a new
        one.  Otherwise, do nothing."""
        result = self.getCurrentResult()
        if result is None:
            suMode = self.userIsGrader(getSecurityManager().getUser())
            if suMode or self.mayResubmit():
                result = createResult(self)
                for group in [self] + self.getQuestionGroups():
                    group.makeNewTest(result, suMode)
                # Make this un-undoable by the candidate
                makeTransactionUnundoable()
            
        return result

    
    security.declarePrivate('syncResults')
    def syncResults(self, action):
        # FIXME: this is a stub
        assert(action in ['move', 'add', 'delete'])
        
        mtool = self.portal_membership
        for result in self.getResults():
            # If this is root's result and it is not submitted, delete
            # it.  Otherwise, possiby mark it as invalid.
            ownerId = result.Creator()
            member = mtool.getMemberById(ownerId)
            ownerIsRoot = self.userIsManager(member)
            if ownerIsRoot and (result.hasState('unsubmitted')):
                self.manage_delObjects([result.getId()])
            elif action != 'move':
                result.tryWorkflowAction('invalidate', ignoreErrors=True)
        
    
#     security.declareProtected(PERMISSION_INTERROGATOR, 'setEvaluationScripts')
#     def setEvaluationScripts(self, evaluationScripts = {}):
#         """ Save the dictionary of custom evaluation scripts in this 
#             instance. 
#         """
#         if( type(evaluationScripts) == dict ):
#             self.evaluationScripts = evaluationScripts
#         else:
#             evaluationScripts = {}
            
        
#     security.declareProtected(PERMISSION_INTERROGATOR,
#                               'processEvaluationScriptUpload')
#     def processEvaluationScriptUpload(self, portal_type, funString):
#         """ Routine for uploading custom evaluation scripts.
        
#             The scripts are stored in the ObjectField
#             'evaluationScripts' of the quiz instance. (That implies
#             every quiz instance can have its own evaluation script.)
            
#             @param portal_type The portal type of the class you
#                    want to customize, e.g. 'ECGroup' or 'ECQuiz'.
                   
#             @param funString A string containing a python script that
#                    can be compiled with Python's 'compile'
#                    function. The script has to define an evaluation
#                    function.  The name of that function has to be what
#                    is specified in the global constant
#                    CUSTOM_EVALUATION_FUNCTION_NAME (see config.py).
#                    See the last line of the 'getCandidatePoints()'
#                    methods of 'ECQuiz', 'ECQGroup'
#                    and 'Question' for the parameters these functions
#                    must accept.
#         """
#         # log("ECQuiz.processEvaluationScriptUpload(\n%s, \n%s)\n"
#         #     %(str(portal_type), funString))
#         try: # Try to compile the script
#             codeObj = compile(funString, '<string>', 'exec')
#         except Exception, e:
#             # Can't be compiled --> not useable
#             errorText = str(e)
#             return errorText
#         noFunctionDefinition = True
#         # Check if the script defines a function whose name is equal to the 
#         # value of the constant 'CUSTOM_EVALUATION_FUNCTION_NAME'
#         if CUSTOM_EVALUATION_FUNCTION_NAME in codeObj.co_names:
#             exec(codeObj)
#             # Check if it is really a function and not a class or var
#             if getattr(eval(CUSTOM_EVALUATION_FUNCTION_NAME),
#                        'func_name', None) == CUSTOM_EVALUATION_FUNCTION_NAME:
#                 noFunctionDefinition = False
#         if noFunctionDefinition:
#             # Either nothing called 'CUSTOM_EVALUATION_FUNCTION_NAME' 
#             # is defined or it's not a function
#             return self.translate(
#                 msgid   = 'uploadEvaluationScript_no_function_definition',
#                 domain  = I18N_DOMAIN,
#                 default = 'The script does not define a function called "%s"')\
#                 % CUSTOM_EVALUATION_FUNCTION_NAME
#         # Save the script in the quiz's 'evaluationScripts' dictionary
#         evaluationScripts = self.getEvaluationScripts()
#         evaluationScripts[portal_type] = funString
#         self.setEvaluationScripts(evaluationScripts)
#         # log("self.evaluationScripts = %s\n"
#         #    %(str(self.getEvaluationScripts())))
#         return None # return no error message (Success)
        
        
    security.declareProtected(PERMISSION_INTERROGATOR, 'processQTIImport')
    def processQTIImport(self, file):
        """ Routine for uploading quizzes.
        
            @param file A file containing a QTI assessmentItem or
                    a QTI package in a zip file.
        """
        addedObjects = []
        errorString = ''
        errors = MyStringIO()
        # try zipfile first
        zipFileInstance = None
        try:
            zipFileInstance = ZipFile(file.filename)
        except:
            try:
                zipFileInstance = ZipFile(file)
            except:
                pass
        if(zipFileInstance):
            # is a zip file
            addedObjects = importPackage(self, zipFileInstance, errors)
        else:
            # no zipfile --> maybe XML?
            # reset the file read ptr first
            try:
                file.seek(0)
            except:
                try:
                    file.filename.seek(0)
                except:
                    pass
            string = None
            try:
                string = file.filename.read()
            except:
                try:
                    string = file.read()
                except:
                    pass
            if type(string) not in [str, unicode]:
                # give up, no XML either
                # The file could not be read.
                errors.write( '\n' + self.translate(
                    msgid   = 'file_read_error',
                    domain  = I18N_DOMAIN,
                    default = 'The file could not be read.') )
            else:
                # is an XML file
                addedObjects = importAssessmentItem(self, string, errors)
        # Reset the read ptr of the StringIO obj
        errors.seek(0)
        errorString = errors.read().strip()
        # log(errorString + '\n')
        return addedObjects, ([errorString, None][not errorString])
        
        
    security.declareProtected(PERMISSION_INTERROGATOR, 'processQTIImport')
    def processQTIExport(self):
        """ Routine for downloading quizzes.
        """
        errors = MyStringIO()
        package = exportPackage(self, errors)
        # Reset the read ptr of the StringIO obj
        errors.seek(0)
        errorString = errors.read().strip()
        # log(errorString + '\n')
        return package, ([errorString, None][not errorString])


    security.declarePublic('getResultsDict')
    def getResultsDict(self, resultUIDList=None):
        """Collect all results objects that meet all of the following
        criteria:
        
           * if [resultUIDList] is not None, then their UID is in
             [resultUIDList]
             
           * their workflow state is acceptable, i. e. one of
             [acceptableStates]
             
           * [member] has the 'View' permission for them

        @return A dictionary { candidateId : list_of_results }
        """
        
        acceptableStates = ('unsubmitted',
                            'graded',
                            'pending',
                            'superseded',
                            )
        member = self.portal_membership.getAuthenticatedMember()

        results = {}
        
        for res in self.getResults():
            if (((resultUIDList is None) or (res.getId() in resultUIDList))
                and (res.getWorkflowState() in acceptableStates)
                and member.has_permission('View', res)):
                candidateId = res.Creator()
                tmp = results.get(candidateId, [])
                tmp.append(res)
                results[candidateId] = tmp

        return results


    security.declarePublic('getResultsAsList')
    def getResultsAsList(self, resultUIDList=None):
        """ Routine for exporting candidate results.
            
            @param resultUIDList A list of UIDs of the results you
                want.  If 'resultUIDList' is 'None', all results will be
                returned.
            
            @return A list containing the results as a dictionary (see
                source for details).
                
                The first "result" ('getResultsAsList()[0]') is a
                header row containing the names of the columns
                associated with the keys in the dictionaries
                (e. g. 'Candidate', 'Name', 'Score' etc.).  The actual
                results start at 'getResultsAsList()[1]'.
        """
        
        def formatTime(dateTimeObj):
            # 'localized_time' is a Plone function
            return localized_time( dateTimeObj, long_format = True,
                                   context = self )
        
        # log("ECQuiz.getResultsAsList()\n")
        ecq_tool = getToolByName(self, 'ecq_tool')

        haveGradingScale = self.haveGradingScale()

        # The header row
        retVal = [
            {'result'      : None, # for internal use only, not used for
                                   # export
             'user_id'     : self.translate(msgid   = 'user_id',
                                            domain  = I18N_DOMAIN,
                                            default = 'User ID'),
             'full_name'   : self.translate(msgid   = 'candidate',
                                            domain  = I18N_DOMAIN,
                                            default = 'Candidate'),
             'state'       : self.translate(msgid   = 'State',
                                            domain  = 'plone',
                                             default = 'State'),
             'grade'       : self.translate(msgid   = 'Grade',
                                            domain  = I18N_DOMAIN,
                                            default = 'Grade'),
             'score'       : self.translate(msgid   = 'test_results_score',
                                            domain  = I18N_DOMAIN,
                                            default = 'Score'),
             'max_score'   : self.translate(msgid   = 'test_results_max_score',
                                            domain  = I18N_DOMAIN,
                                            default = 'Max. Score'),
             'time_start'  : self.translate(msgid   = 'started',
                                            domain  = I18N_DOMAIN,
                                            default = 'Started'),
             'time_finish' : self.translate(msgid   = 'finished',
                                            domain  = I18N_DOMAIN,
                                            default = 'Finished'),
             }]
        
        if not haveGradingScale:
            retVal[0].pop('grade')

        # Get the results
        results = self.getResultsDict(resultUIDList=resultUIDList)
        
        # Remove unsubmitted results of candidates that also have
        # submitted results
        for resList in results.values():
            if len(resList) > 1:
                for res in resList:
                    if res.hasState('unsubmitted'):
                        resList.remove(res)
                        break
        
        participants  = results.keys()
        # We only want submitters who are also in the list of participants 
        # (i.e. in [participants])
        submitters = [c for c in self.getSubmitterIds()
                      if c in participants]
        # Participants who have not submitted their quizzes
        nonSubmitters = [c for c in participants
                         if c not in submitters]
        #log("participants: %s\nsubmitters: %s\nnonSubmitters: %s\n\n"
        #    %(str(participants), str(submitters), str(nonSubmitters)))
        
        # Sort 'participants' so that 'submitters' come first
        submitters.sort(ecq_tool.cmpByName)
        nonSubmitters.sort(ecq_tool.cmpByName)
        participants  = submitters + nonSubmitters

        # The result workflow
        resultWf = self.portal_workflow.getWorkflowById(ECMCR_WORKFLOW_ID)

        member = getSecurityManager().getUser()
        memberId = member.getId()
        
        # The content rows
        for participantId in participants:
            for result in results[participantId]:
                state  = result.getWorkflowState()
                stateTitle = resultWf.states[state].title
                i18nStateTitle = self.translate(msgid   = stateTitle,
                                                domain  = 'plone',
                                                default = stateTitle)

                grade = None
                points = None
                possiblePoints = self.getPossiblePoints(result)
                if state != 'unsubmitted':
                    timeFinished = formatTime( result.getTimeFinish() )
                    # If [member] is the owner of the current quiz,
                    # return the points only if he explicitly has the
                    # permission to see them.
                    if ((participantId != memberId)
                        or self.userIsGrader(member)
                        or self.isInstantFeedback()
                        or ecq_tool.userHasOneOfRoles(
                               member,
                               (ROLE_RESULT_VIEWER,),
                               result)):
                        
                        # I18N floating point numbers is not done
                        # because exportResults.py needs to know that
                        # when it does the CVS export
                        points = self.getCandidatePoints(result)
                        if haveGradingScale:
                            grade = self.getCandidateGrade(result)
                else:
                    timeFinished = self.translate(msgid   = 'not_submitted',
                                                  domain  = I18N_DOMAIN,
                                                  default = 'Not submitted')
                
                retVal.append(
                    {'result'      : result,
                     'user_id'     : participantId,
                     'full_name'   : ecq_tool.getFullNameById(participantId),
                     'state'       : i18nStateTitle,
                     'grade'       : grade,
                     'score'       : points,
                     'max_score'   : possiblePoints,
                     'time_start'  : formatTime( result.getTimeStart() ),
                     'time_finish' : timeFinished,
                     })
                if not haveGradingScale:
                    retVal[-1].pop('grade')

        return retVal
        
        
    security.declareProtected(PERMISSION_GRADE, 'getItemStatisticsW')
    def getItemStatisticsW(self, candidateIdList = None):
        """ Routine for exporting detailed candidate results.
            
            @return A list of containing the results as a list of values. The
                values appear in the following order:
                
                [CandidateID, Candidate_Name] followed by either -, 0 or 1 for
                each answer to each question in each question group in the
                quiz.
                
                "-" means the candidate did not have this answer presented to
                him/her as a possibility, "0 "means he/she did see this answer
                but did not check it and "1" means he/she did check it.
                
                The first three "results" are header rows.
        """
        ecq_tool = getToolByName(self, 'ecq_tool')

        # The header row
        retVal = []
        h1 = ['', '']
        h2 = ['', '']
        h3 = [self.translate(msgid = 'candidate',
                             domain  = I18N_DOMAIN,
                             default = 'Candidate'),
              self.translate(msgid = 'name',
                             domain  = I18N_DOMAIN,
                             default = 'Name')]
        for group in [self] + self.getQuestionGroups():
            h1.append([group.title_or_id(),
                       self.translate(msgid = 'ungrouped',
                                      domain  = I18N_DOMAIN,
                                      default = '(Ungrouped)')
                       ][group is self])
            allQuestions = group.getAllQuestions()
            numQuestions = len(allQuestions)
            for question in allQuestions:
                numAnswers = len(question.listFolderContents())
                h1 += ['' for i in range(numAnswers)]
                h2 += [question.title_or_id()] \
                     + ['' for i in range(numAnswers-1)]
                h3 += ['a%d' % (i+1) for i in range(numAnswers)]
            # we added one placeholder too much in the loop above
            h1 = h1[:-1]
        
        for h in [h1, h2, h3]:
            retVal.append( h )
            
        # The content rows
        submitters = self.getSubmitterIds()
        if candidateIdList is not None:
            # If not all results are requested, filter 'submitters' so that
            # every 'candidateId' in 'submitters' is also in 'candidateIdList'
            submitters = filter((lambda candidateId :
                                 (candidateId in candidateIdList)), submitters)
        submitters.sort()
        NaN           = '-' # Not a number/not available
        for submitterId in submitters:
            row = [submitterId, ecq_tool.getFullNameById(submitterId)]
            for group in [self] + self.getQuestionGroups():
                for question in group.getAllQuestions():
                    sSuggestedAnswerIds = question.getSuggestedAnswerIds(
                        submitterId) or []
                    #log(str(sSuggestedAnswerIds))
                    sCandidateAnswerIds = question.getCandidateAnswer(
                        submitterId) or []
                    #log(str(sCandidateAnswerIds))
                    for answer in question.listFolderContents():
                        aId = answer.getId()
                        row += [
                            [NaN, [0, 1][aId in sCandidateAnswerIds]][
                            aId in sSuggestedAnswerIds]]
            
            retVal.append( row )

        #log(self.unicodeDecode(retVal))

        return retVal
    
    
    def getItemStatisticsTable(self, keepQuestionGroups=False):
        data = self.getItemStatistics2(keepQuestionGroups)
        participants  = self.getParticipantIds()
        submitters    = filter((lambda candidateId:
                                (candidateId in participants)),
                               self.getSubmitterIds())
        submitters.sort()

        #
        questions = self.getAllQuestions()

        if keepQuestionGroups:
            questions += self.getQuestionGroups()
        else:
            for group in self.getQuestionGroups():
                questions += group.getAllQuestions()

        infoByQid = {}
        for q in questions:
            if shasattr(q, 'getPoints'):
                infoByQid[q.getId()] = {'max': q.getPoints(),
                                        'title': q.getTitle()}
            else:
                infoByQid[q.getId()] = {'max': 'unknown',
                                        'title': q.getTitle()}
        #

        table = []
        #table.append(['questions'] + data.keys())

        row = ['_items']
        for qid in data.keys():
            row.append(infoByQid[qid]['title'])
        table.append(row)

        row = ['_ids']
        for qid in data.keys():
            row.append(qid)
        table.append(row)

        row = ['_max']
        for qid in data.keys():
            row.append(infoByQid[qid]['max'])
        table.append(row)

        for candidateId in submitters:
            row = [candidateId] + ['-' for i in range(len(data.keys()))]
            
#             for i in range(len(data.keys())):
#                 for submission in data[data.keys()[i]]:
#                     if submission[0] == candidateId:
#                         row[i + 1] = submission[1]

            i=1
            for value in data.values():
                for submission in value:
                    if submission[0] == candidateId:
                        row[i] = submission[1]
                i+=1
            
            table.append(row)
        
        return table

    
    security.declarePublic('haveDetailedScores')
    def haveDetailedScores(self):
        for item in self.getResults():
            if item.hasState('graded'):
                return True
        return False
    

    def getDetailedScores(self):
        # no doc string to disable publishing

        ecq_tool = getToolByName(self, 'ecq_tool')
        haveGradingScale = self.haveGradingScale()

        results = {}
        for item in self.getResults():
            if item.hasState('graded'):
                results[item.Creator()] = item
                
        submitters = results.keys()
        submitters.sort(ecq_tool.cmpByName)
        
        table = []

        labels = {}
        for msgid in [('candidate', 'Candidate'),
                      ('grade',     'Grade'),
                      ('test_results_max_score', 'Max. Score'),
                      ('N', 'Number'),
                      ('sample', 'Sample'),
                      ('mean', 'Mean'),
                      ('median', 'Median'),
                      ('stddev', 'Std. Dev.')]:
            labels[msgid[0]] = self.translate(msgid = msgid[0],
                                              domain = I18N_DOMAIN,
                                              default = msgid[1])
        
        header    = [(labels['candidate'], '', '')]
        maxScores = [labels['test_results_max_score']]
        if haveGradingScale:
            header.append((labels['grade'], '', ''))
            maxScores.append('')
        
        if results:
            result0 = results.values()[0]
        else:
            result0 = None

        for group in [self] + self.getQuestionGroups():
            header.append((group.title_or_id(),
                           group.archetype_name,
                           group.reference_url()))
            if result0:
                maxScore = group.getPossiblePoints(result0)
            else:
                maxScore = '-'
            maxScores.append(maxScore)
            
            allQuestions = group.getAllQuestions()
            
            for question in allQuestions:
                header.append((question.title_or_id(),
                               question.archetype_name,
                               question.reference_url()))
                maxScores.append(question.getPoints())
        
        table.append(header)
        
        if not submitters:
            return table
        
        for cand in submitters:
            result = results[cand]
            candRow = [cand]
            if haveGradingScale:
                candRow.append(self.getCandidateGrade(result))

            for group in [self] + self.getQuestionGroups():
                candRow.append(group.getCandidatePoints(result))
                
                allQuestions       = group.getAllQuestions()
                suggestedQuestions = group.getQuestions(result)
                
                for question in allQuestions:
                    if question in suggestedQuestions:
                        val = question.getCandidatePoints(result)
                    else:
                        val = 1000000 # FIXME: what to do in this case?
                    candRow.append(val)
                
            table.append(candRow)
        
        # Prepare statistics
        
        temp = []
        stats_input = []
        for col in range((haveGradingScale and 2) or 1, len(header)):
            for row in table[1:]:
                stats_input.append(row[col])
            temp.append(stats_input)
            stats_input = []
        
        table.append(maxScores)
        
        for analysis in ['mean', 'median', 'stddev']:
            statsRow = [labels[analysis]]
            if haveGradingScale:
                statsRow.append('')
            for set in temp:
                stats = Statistics(set)
                statsRow.append(getattr(stats, analysis))
            table.append(statsRow)

        return table
    

    def getItemStatistics3(self):
        participants = self.getParticipantIds()
        table = []

        for group in [self] + self.getQuestionGroups():
            table.append(group.title_or_id)
            allQuestions = group.getAllQuestions()
            numQuestions = len(allQuestions)
            
            for question in allQuestions:
                numAnswers = len(question.listFolderContents())
                header = [question.title_or_id(), 'N', '-'] + \
                         [str(i + 1) for i in range(numAnswers)] + \
                         ['mean', 'stddev', 'median', 'mode']

                i = 3
                for answer in question.listFolderContents():
                    if answer.isCorrect():
                        header[i] += '*'
                    i += 1
                
                
                submitters = [candId for candId in self.getSubmitterIds()
                              if candId in participants]
                afreqs = [question.title_or_id(), 0, 0] + \
                         [0 for i in range(numAnswers)]
                
                for submitter in submitters:
                    sSuggestedAnswerIds = question.getSuggestedAnswerIds(
                        submitter) or []
                    sCandidateAnswerIds = question.getCandidateAnswer(
                        submitter) or []
                    
                    if not sCandidateAnswerIds:
                        afreqs[2] += 1
                    else:
                        afreqs[1] += 1 # Number of candidates

                        i = 3
                        for answer in question.listFolderContents():
                            aid = answer.getId()
                            afreqs[i] += [0, 1][aid in sCandidateAnswerIds]
                            i += 1

                # Prepare statistics
                i = 1
                items = []
                for freq in afreqs[3:]:
                    items.extend([i for n in range(0, freq)])
                    i += 1

                stats = Statistics(items)
                afreqs.append(stats.mean)
                afreqs.append(stats.stddev)
                afreqs.append(stats.median)
                afreqs.append(stats.mode)

                table.append(header)
                table.append(afreqs)
                    
        return table

    def getItemStatistics2(self, keepQuestionGroups=False):
        participants  = self.getParticipantIds()
        submitters    = [candId for candId in self.getSubmitterIds()
                         if candId in participants]
        submitters.sort()

        questions = self.getAllQuestions()

        if keepQuestionGroups:
            questions += self.getQuestionGroups()
        else:
            for group in self.getQuestionGroups():
                questions += group.getAllQuestions()

        itemStats = {}
        for q in questions:
            itemStats[q.getId()] = []

        for candidateId in submitters:
            candQuestions = self.getQuestions(candidateId)

            for group in self.getQuestionGroups():
                if keepQuestionGroups:
                    candQuestions += self.getQuestionGroups()
                else:
                    candQuestions += group.getQuestions(candidateId)
            
            for q in candQuestions:
                if hasattr(q, 'getPoints'):
                    max = q.getPoints()                    # Question
                else:
                    max = q.getPossiblePoints(candidateId) # Question group
                
                itemStats[q.getId()].append((candidateId,
                                             q.getCandidatePoints(candidateId),
                                             max))
        
        return itemStats
    
    def getItemStatistics(self, keepQuestionGroups=False):
        participants  = self.getParticipantIds()
        submitters    = [candId for candId in self.getSubmitterIds()
                         if candId in participants]
        submitters.sort()

        x = {}
        for candidateId in submitters:
            x[candidateId] = []
            
            questions      = self.getQuestions(candidateId)
            questionGroups = self.getQuestionGroups()
            for q in questions:
                max = q.getPoints()
                x[candidateId].append((q.getTitle(),
                                       q.getCandidatePoints(candidateId),
                                       max))
            for q in questionGroups:
                if keepQuestionGroups:
                    max = q.getPossiblePoints(candidateId)
                    x[candidateId].append((q.getTitle(),
                                           q.getCandidatePoints(candidateId),
                                           max))
                else:
                    contained = q.getQuestions(candidateId)
                    for q in contained:
                        max = q.getPoints()
                        x[candidateId].append((q.getTitle(),
                                               q.getCandidatePoints(candidateId),
                                               max))
        return x
    
            
    def getQuestionGroups(self):
        """ Returns all the ECQGroup elements (no single questions). """
        return [o for o in self.mcContentValues()
                if o.portal_type == ECQGroup.portal_type]


    security.declarePublic('isEmpty')
    def isEmpty(self):
        return (not self.getQuestionGroups()) and \
               (not self.getAllQuestions())
        
    security.declarePrivate('computePossiblePoints')
    def computePossiblePoints(self, result):
        """ Return how many points the candidate could have got.
            
            @param candidateId the user ID of the candidate whose points you 
                    want to know. 
        """
        points = ECQAbstractGroup.computePossiblePoints(self, result)
        if not isNumeric(points):
            return None
        questionGroups = self.getQuestionGroups()
        for questionGroup in questionGroups:
            questionGroupPoints = questionGroup.getPossiblePoints(result)
            if not isNumeric(questionGroupPoints):
                return None
            points += questionGroupPoints
        return points
            
    security.declarePrivate('computeCandidatePoints')
    def computeCandidatePoints(self, result):
        """ Return how many points the candidate got for this quiz.
            
            @param candidateId the user ID of the candidate whose
            points you want to know.
            
            If a custom evaluation script has been uploaded it will be
            invoked. Otherwise a default method will be used. 
        """
        customScript = self.getEvaluationScript(self.portal_type)
        questions = self.getQuestions(result)
        questionGroups = self.getQuestionGroups()
        if not customScript: # default
            points = 0
            for questionGroup in questionGroups:
                questionGroupCandidatePoints = \
                    questionGroup.getCandidatePoints(result)
                if not isNumeric(questionGroupCandidatePoints):
                    return None
                points = points + questionGroupCandidatePoints
            for question in questions:
                if not shasattr(question, 'getCandidatePoints'):
                    return None
                questionCandidatePoints = \
                    question.getCandidatePoints(result)
                if not isNumeric(questionCandidatePoints):
                    return None
                points = points + questionCandidatePoints
            return points
        else: # custom
            return evalFunString(
                customScript, CUSTOM_EVALUATION_FUNCTION_NAME,
                [self, candidateId, questionGroups, questions])

    security.declareProtected(PERMISSION_GRADE, 'setGradingScale')
    def setGradingScale(self, input):
        """
        Mutator for the `gradingScale' field.  Allows the input of
        localized numbers in the Minimum Score column.
        """
        decimalSeparator = self.translate(msgid = 'fraction_delimiter',
                                          domain = I18N_DOMAIN,
                                          default = '.')
        mutated = []
        
        for row in input:
            if row.has_key('score'): # Initially empty
                score = row['score'].strip()
                newrow = row.copy()
                match = re.match('^[0-9]+(\\' + decimalSeparator
                                 + ')?[0-9]*\s*%?$', score)
                if match:
                    score = score.replace(decimalSeparator, '.')
                    newrow['score'] = score

                mutated.append(newrow)

        self.getField('gradingScale').set(self, mutated)


    def getGradingScaleForEdit(self):
        """
        Edit accessor for the `gradingScale' field. Converts the
        stored minimum score to localized representation.
        """
        stored_data = self.getGradingScale()
        mctool      = getToolByName(self, 'ecq_tool')
        for_edit    = []

        for row in stored_data:
            newrow = row.copy()
            score  = row['score']
            
            match = re.match('^([0-9.]+)(\s*%)?$', score)
            if match:
                number = match.group(1)
                prec = 0
                if number.find('.') > 0:
                    prec = len(number) - number.find('.') - 1

                newrow['score'] = mctool.localizeNumber('%.*f',
                                                        (prec, float(number)))
                if (match.group(2)):
                    newrow['score'] += match.group(2)
            
            for_edit.append(newrow)
        
        return for_edit

    
    security.declarePrivate('haveGradingScale')
    def haveGradingScale(self):
        for item in self.getGradingScale():
            if item['score'].strip() or item['grade'].strip():
                return True
        return False
        
        
    #security.declarePrivate('')
    def getCandidateGrade(self, result):
        # (no doc-string to disable publishing)
        #
        # Return the candidate's grade according to the grading scale
        # or None.
        
        points = self.getCandidatePoints(result)
        if (points is not None) and self.haveGradingScale():
            scale = []
            for item in self.getGradingScale():
                d = dict(item)

                if d['score'].endswith('%'):
                    num = float((d['score'].split('%'))[0])
                    f = self.computePossiblePoints(result)/100.0 * num
                else:
                    try:
                        f = float(d['score'])
                    except ValueError:
                        f = None
                d['score'] = f
                scale.append(d)

            def comp(a, b):
                as = a['score']
                bs = b['score']
                if as is None:
                    return 1
                elif bs is None:
                    return -1
                else:
                    return as > bs
            
            scale.sort(comp)

            for pair in scale:
                minScore = pair['score']
                if (minScore is None) or (points >= minScore):
                    grade = pair['grade']
                    for conv in int, float:
                        try:
                            return conv(grade)
                        except:
                            pass
                    return grade
        
        return None

                
    #security.declarePrivate('')
    def getCandidateGradeinfo(self, result):
        # (no doc-string to disable publishing)
        #
        # Return the candidate's grade according to the grading scale
        # or None.
        
        points = self.getCandidatePoints(result)
        if (points is not None) and self.haveGradingScale():
            scale = []
            for item in self.getGradingScale():
                d = dict(item)

                if d['score'].endswith('%'):
                    num = float((d['score'].split('%'))[0])
                    f = self.computePossiblePoints(result)/100.0 * num
                else:
                    try:
                        f = float(d['score'])
                    except ValueError:
                        f = None
                d['score'] = f
                scale.append(d)

            def comp(a, b):
                as = a['score']
                bs = b['score']
                if as is None:
                    return 1
                elif bs is None:
                    return -1
                else:
                    return as > bs
            
            scale.sort(comp)

            for pair in scale:
                minScore = pair['score']
                if (minScore is None) or (points >= minScore):
                    val = pair['gradeinfo'].strip()
                    if val == "":
                        return None
                    return val
        
        return None

                
    def getWorkflowState(self):
        """ Determine the Plone workflow state. """
        workflow_tool = getToolByName(self, 'portal_workflow')
        return workflow_tool.getInfoFor(self, 'review_state', None)
        
        
    # This function has to be implemented by classes derived from 
    # ECQAbstractGroup
    security.declarePublic('isPublic')
    def isPublic(self):
        """ Determine whether this quiz has been published. """
        # log('ECQuiz.isPublic():\n')
        try:
            user = getSecurityManager().getUser()
            showUnpublishedContent = user.has_role('Authenticated') and \
                                     ('Manager' in self.get_local_roles_for_userid(user.getId()) \
                                      or user.has_role('Manager'))

            # log('\tshowUnpublishedContent = %s\n'
            #     %(str(showUnpublishedContent)))
            if showUnpublishedContent:
                return True
            if self.getWorkflowState() != 'published':
                # log("\t!'published'\n")
                return False
            now            = DateTime()
            startPublished = getattr(self, 'effective_date', None)
            endPublished   = getattr(self, 'expiration_date', None)
            # log('\tnow = ' + str(now) + '\n')
            # log('\tstartPublished = ' + str(startPublished) + '\n')
            # log('\tendPublished = ' + str(endPublished) + '\n')
            if((startPublished != None) and (startPublished > now)):
                # log("\tstartPublished > now\n")
                return False
            if((endPublished != None) and (now > endPublished)):
                # log("\tnow > endPublished\n")
                return False
            # log("\treturn True\n")
            return True
        except:
            # log("ECQuiz.isPublic() failed. An unknown "
            #     "exception occurred.\n")
            # log("\treturn False\n")
            return False        

    
    security.declareProtected(PERMISSION_INTERROGATOR, 'deleteResultsById')
    def deleteResultsById(self, resultIdList):
        """Deletes all the results whose id is in [resultIdList]."""
        self.manage_delObjects(resultIdList)


    security.declareProtected(PERMISSION_INTERROGATOR,
                              'unsetCachedQuestionPoints')
    def unsetCachedQuestionPoints(self, question):
        results = self.getResults()
        for result in results:
            result.unsetCachedQuestionPoints(question)


    security.declareProtected(PERMISSION_INTERROGATOR, 'unsetAllCachedPoints')
    def unsetAllCachedPoints(self):
        results = self.getResults()
        for result in results:
            result.unsetAllCachedPoints()
            
        
    def pre_validate(self, REQUEST, errors):
        """ This function is called when submitting the edit form (base_edit).
            
            @param REQUEST Contains the input for the form.
            @param errors If any validation error occurs, put it here.
                
            Requests from the 'base_edit' form to delete custom 
            evaluation scripts (from ObjectField 'evaluationScripts') 
            are processed here. 
        """
        if REQUEST.get('deleteCustomEvaluationScripts', []) != []:
            scriptsToBeDeleted = REQUEST.get('deleteCustomEvaluationScripts',
                                             [])
            if type(scriptsToBeDeleted) != list:
                scriptsToBeDeleted = [scriptsToBeDeleted]
            evaluationScripts = self.getEvaluationScripts()
            for portal_type in scriptsToBeDeleted:
                if evaluationScripts.has_key(portal_type):
                    evaluationScripts.pop(portal_type)
            self.setEvaluationScripts(evaluationScripts)
            
            
    # def post_validate(self, REQUEST, errors):
        # if(REQUEST.get('sourceFile_file', False)):
            # sourceFile = REQUEST.get('sourceFile_file')
            # try:
                # string = sourceFile.filename.read()
            # except:
                # string = sourceFile.read()
            # errorMsg = self.processQTIImport(string)
            # if(errorMsg):
                # errors['sourceFile'] = errorMsg + ' File=' + string
            # self.setSourceFile(None)
            

    security.declareProtected(PERMISSION_INTERROGATOR, 'convertQuiz')
    def convertQuiz(self, quiz):
        return wikitool.convertQuiz(quiz)

    security.declareProtected(PERMISSION_INTERROGATOR, 'updateQuiz')
    def updateQuiz(self, quiz, wikistyle):
        return wikitool.updateQuiz(quiz, wikistyle)

    security.declareProtected(PERMISSION_INTERROGATOR, 'importQuiz')
    def importQuiz(self, quiz, filename):
        return wikitool.importQuiz(quiz, filename)

    security.declareProtected(PERMISSION_INTERROGATOR, 'exportQuiz')
    def exportQuiz(self, quiz, filename):
        return wikitool.exportQuiz(quiz, filename)
            
# Register this type in Zope
registerATCTLogged(ECQuiz)
