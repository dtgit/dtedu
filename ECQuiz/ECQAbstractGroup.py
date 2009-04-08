# -*- coding: iso-8859-1 -*-
#
# $Id: ECQAbstractGroup.py,v 1.3 2006/10/19 19:21:47 wfenske Exp $
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

from DateTime import DateTime

from AccessControl import ClassSecurityInfo
import Acquisition
from Acquisition import *

from Products.Archetypes.utils import shasattr
from Products.Archetypes.public import BaseFolderSchema, Schema, \
     BooleanField, IntegerField, StringField, TextField, \
     TextAreaWidget
#from Products.ATContentTypes.content.base import updateActions, updateAliases
from Products.Archetypes.Widget import TypesWidget, BooleanWidget, \
     IntegerWidget, RichWidget

from Products.CMFCore.utils import getToolByName

from config import *
from permissions import *
from tools import *
from ECQReference import ECQReference
from ECQFolder import ECQFolder


class ReferenceWrapper(Acquisition.Implicit):
    def __getattr__(self, key):
        #log("__getattr__(%s, %s)\n" %(str(self), str(key)))
        # Otherwise we get into an endless recursion--for whatever
        # reason ...
        if key in ["__methods__", "__members__"]:
            raise AttributeError("'%s' object has no attribute '%s'"
                                 %(repr(self), str(key)))
        else:
            # Acquire the attribute from the referenced object
            # ([self.refObj]), pretending that its parent is
            # [self.parent].
            return self.refObj.__of__(self.parent).aq_acquire(key)
        
    
    def __init__(self, parent, refObj):
        # don't rename the 'parent' attribute unless you change the
        # name in tools.getParent() as well!
        self.parent = parent
        self.refObj = refObj


class ECQAbstractGroup(ECQFolder):
    """An abstract folder-like class that is designed to contain
    question objects.
        
    The derived classes are 'ECQuiz', 'ECQGroup'.
    They contain question objects and thus have common functionality
    which they inherit from this class.
    """

    """The Archetype schema of this type.  It basically describes how
    this class looks like for Zope, i.e.  which properties 'documents'
    of this type have, which types these properties have, which
    widgets should be used for manipulation, which permissions apply
    etc.  Archetypes automatically generates accessors/mutators
    (get/set methods) for all the properties defined in the schema if
    methods with these names do not already exist.  E.g. by defining
    TextField('answer') Archetypes generates 'getAnswer()' and
    'setAnswer()'.
    """
    schema = ECQFolder.schema.copy() + Schema((
            # Read the 'description_msgid' for explanations of the
            # various properties of this type
            TextField(
                # The Python name of this property (i.e. in Python
                # code it can be accessed via 'self.directions')
                "directions",
                # This property does not have to be entered if a new
                # document of this type is created.
                required=False,
                # Text in various formats can be entered
                allowable_content_types=('text/plain',
                                         'text/structured',
                                         'text/restructured',
                                         'text/html',),
                # Output the field's contents as HTML by
                # default. Otherwise HTML elements will simply be
                # stripped.  To see formatted ouput, you also need to
                # put the keyword "structure" in front of the call to
                # the getter method, in the corresponding page
                # template. Write something like
                #
                # <span tal:replace="structure here/getDirections">
                #   Directions</span>
                # instead of <span tal:replace="here/getDirections">Directions
                #   </span>
                #
                # which is how you normally access the contents of a
                # field.
                default_output_type='text/html',
                widget=TextAreaWidget(
                    # Default label of this property.  This is the
                    # name used for this property in e.g. the
                    # base_edit view of a document of this type.
                    label='Directions',
                    # label_msgid of this property (used for
                    # internationalization)
                    label_msgid='directions_label',
                    # Default description of this property This
                    # description will be the tool tip displayed for
                    # this property in e.g. the base_edit view of a
                    # document of this type.
                    description='Some content that all the questions in '
                    'this folder refer to. You can also enter a text '
                    'which helps the candidates to better understand '
                    'the questions.',
                    # description_msgid of this property (used for
                    # internationalization)
                    description_msgid='directions_tool_tip',
                    # The internationalization domain for this
                    # property, i.e. the namespace for label_msgid and
                    # description_msgid.  This namespace is defined
                    # via "Domain: ECQuiz\n" in the
                    # .po/.pot-files in the 'i18n' directory.
                    i18n_domain=I18N_DOMAIN),
                validators=('isXML',),
                read_permission=PERMISSION_STUDENT,
            ),
            BooleanField("randomOrder",
                # Specify an accessor for this property named differently
                # than the standard accessor ('getRandomOrder()' or so)
                #  that Archetypes would have generated
                accessor='isRandomOrder',
                required=False,
                # Default to 'True'
                # Working with '0' and '1' instead of 'False' and 'True'
                # seems to work better with Archetypes.
                default=1,
                # This property may not be read by user with lower
                # privileges than PERMISSION_INTERROGATOR (see
                # config).  That means a
                # user with PERMISSION_STUDENT will not see this
                # property when he/she # calls e.g. the base_view page
                # template.
                read_permission=PERMISSION_INTERROGATOR,
                widget=BooleanWidget(
                    label='Randomize Question Order',
                    label_msgid='randomize_question_order_label',
                    description='Check this box if you want the questions '
                    'in this container to appear in a different, random '
                    'order for each candidate. Otherwise the same order '
                    'as in the &quot;contents&quot;-view will be used.',
                    description_msgid='randomize_question_order_tool_tip',
                    i18n_domain=I18N_DOMAIN),
            ),
            IntegerField("numberOfRandomQuestions",
                required=False,
                default=-1,
                read_permission=PERMISSION_INTERROGATOR,
                widget=IntegerWidget(
                    label='Number of Random Questions',
                    label_msgid='number_of_random_questions_label',
                    description='The number of questions which are randomly '
                        'selected when a new quiz is '
                        'generated for a candidate. (This only works if '
                        '&quot;Randomize Question Order&quot; '
                        'is checked.) A value &lt;= 0 means that all '
                        'questions will be used.',
                    description_msgid='number_of_random_questions_tool_tip',
                    i18n_domain=I18N_DOMAIN),
            ),
        ),)

    """Register custom Page Templates for specific actions, e.g.
    'view', 'edit' or self defined actions."""
    suppl_views = None
    default_view = immediate_view = 'ecq_group_view'
    
#    aliases = updateAliases(ECQFolder, {
#        'view': default_view,
#        })
    

    # The Zope name of this type
    meta_type = 'ECQAbstractGroup'    # zope type name
    portal_type = meta_type           # plone type name
    archetype_name = 'Abstract Group' # friendly type name

    
    """'Standalone' documents of this type are not allowed. Documents
    of this type are allowed only as part of certain other types of
    documents, i.e. those, whose 'allowed_content_types' property (see
    below) is set to something like
    'tuple(['ECQAbstractGroup'])'.  That means you cannot
    create an 'ECQAbstractGroup' instance directly on the
    start page but only as content in other (folder-like) documents.
    """
    global_allow = False
    """ 'ECQAbstractGroup' documents can only contain other
    documents of the types specified in the list QUESTION_TYPES (see
    config).
    """
    
    allowed_content_types = ('ECQMCQuestion',
                             'ECQExtendedTextQuestion',
                             'ECQScaleQuestion',
                             ECQReference.portal_type)
        
    # Get a ClassSecurityInfo-instance in order to declare some class
    # methods protected or private
    security = ClassSecurityInfo()

    # The following functions would have to be implemented by derived
    # classes but through Zope's acquisition, we get exactly what we
    # want for free.

    # def getResults(self):
    # def isPublic(self):
    # def getEvaluationScripts(self):
    
    
    security.declarePrivate('getAllQuestions')
    def getAllQuestions(self):
        """Return all the Question elements (no question groups) which
        are direct children of this folder.
        """
        return [o for o in self.mcContentValues()
                if o.portal_type in ECQAbstractGroup.allowed_content_types]
    

    security.declarePrivate('mcContentValues')
    def mcContentValues(self):
        """Same as 'listFolderContents()' except that for elements of
        type 'ECQReference', the referenced object is returned,
        wrapped in a 'ReferenceWrapper.'
        """
        def getRefOrSelf(obj):
            if obj.portal_type == ECQReference.portal_type:
                refObj = obj.getReference()
                if refObj:
                    obj = ReferenceWrapper(self, refObj)
                else:
                    obj = None
                    
            return obj

        contents = ECQFolder.contentValues(self)
        ret = []
        for o in contents:
            refOrSelf = getRefOrSelf(o)
            if refOrSelf:
                ret.append(refOrSelf)
        return ret


    def _notifyOfCopyTo(self, container, op=0):
        """This method is here, because the 'reference' attribute of
        'ECQReference' objects is not copied by default. So
        we call '_notifyOfCopyTo()' to tell every
        'ECQReference' object to back up its 'reference'
        attribute.

        In Archetypes 1.4, this should not be necessary anymore
        because there will be switch to enable copying the contents of
        ReferenceFields.
        """
        #log("%s._notifyOfCopyTo()\n" % str(self))
        for obj in self.contentValues():
            obj._notifyOfCopyTo(self, op=op)
        return ECQFolder._notifyOfCopyTo(self, container, op=op)


    security.declarePrivate('makeNewTest')
    def makeNewTest(self, candidateResult, suMode):
        """Generates a new quiz for the candidate.
        """
        # Select the questions
        allQuestions = self.getAllQuestions()
        if self.isRandomOrder() and (not suMode):
            # use random order
            numRnd = min(len(allQuestions), self.getNumberOfRandomQuestions())
            if numRnd > 0:
                sampleSz = numRnd
            else:
                sampleSz = len(allQuestions)
            questions = random.sample(allQuestions, sampleSz)
        else:
            # use the order in the "contents"-view
            questions = allQuestions

        # Call makeNewTest() on each selected question
        for q in questions:
            q.makeNewTest(candidateResult, suMode)
        

    security.declareProtected(PERMISSION_STUDENT, 'getQuestions')
    def getQuestions(self, result):
        """Returns the actual question objects that the candidate saw
        in his/her quiz and in the order they were presented
        """
        # reconstruct the old quiz
        questionIds = result.getQuestionUIDs()
        # reconstruct the order of the questions
        retVal = filterByUID(questionIds, self.getAllQuestions())
        #log('\t   questions = ' + repr(retVal) + '\n')
        return retVal

    
    security.declareProtected(PERMISSION_STUDENT, 'haveCandidateAnswer')
    def haveCandidateAnswer(self, result):
        questions = self.getQuestions(result)
        for q in questions:
            if not q.haveCandidateAnswer(result):
                return False
        return True


    def getPossiblePoints(self, result):
        """Return how many points the candidate could have got, which
        is the sum of points for all the questions in this container
        (not recursively).

        @param candidateId the user ID of the candidate whose points
        you want to know.
        """
        # Check if we have a cached value
        retVal = result.getCachedPossiblePoints(self)
        if retVal is None:
            retVal = self.computePossiblePoints(result)
            result.setCachedPossiblePoints(self, retVal)
        return retVal
    
    
    security.declarePrivate('computePossiblePoints')
    def computePossiblePoints(self, result):
        questions = self.getQuestions(result)
        points = 0
        for question in questions:
            if not shasattr(question, 'getPoints'):
                return None
            questionPoints = question.getPoints()
            if not isNumeric(questionPoints):
                return None
            points = points + questionPoints
        return points


    def getCandidatePoints(self, result):
        """ Return how many points the candidate got for this quiz.
            
            @param candidateId the user ID of the candidate whose
            points you want to know.
            
            If a custom evaluation script has been uploaded it will be
            invoked. Otherwise a default method will be used. 
        """
        # Check if we have a cached value
        retVal = result.getCachedCandidatePoints(self)
        if retVal is None:
            retVal = self.computeCandidatePoints(result)
            result.setCachedCandidatePoints(self, retVal)
        return retVal


    security.declarePublic('isTutorGraded')
    def isTutorGraded(self, result):
        for q in self.getQuestions(result):
            if shasattr(q, 'isTutorGraded') and q.isTutorGraded():
                return True
        return False


    def getEvaluationScript(self, archetype_name):
        """Return the custom evaluation script that has been uploaded
        for the class with Archetype Name archetype_name or None if no
        script has been uploaded.

        @param archetype_name The Archetype Name of the class.
        """
        return None

        
        evaluationScripts = self.getEvaluationScripts()
        if(evaluationScripts.has_key(archetype_name)):
            return evaluationScripts[archetype_name]
        else:
            return None

    def getEvaluationScriptComment(self, archetype_name):
        """TODO"""
        script = self.getEvaluationScript(archetype_name)
        if script:
            d = {}
            code = compile(script, '<string>', 'exec')
            exec code in d
            return d[CUSTOM_EVALUATION_FUNCTION_NAME].__doc__
        else:
            return None


# Register this type in Zope
registerATCTLogged(ECQAbstractGroup)
