# Copyright 2006 Otto-von-Guericke-Universit�t Magdeburg
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

from StringIO import StringIO
from l2 import *                # Wolfram Fenske's Lisp2Python parser
from time import time
from random import random

### UPDATE STUFF ####################################


def updateQuiz(quiz, wikistyle):
        """Will update an ECQuiz object.

        The method takes the provided wiki-syntax data and updates an ECQuiz.

        Parameters:
                quiz            - The ECQuiz object to update
                wikistyle       - A string"""

        try:
                token_list = Tokenizer().tokenize(wikistyle)
        except TokenizerError, te:
                return "TokenizerError: " + str(te)
        try:
                parse_tree = Parser().parse(token_list)
        except ParserError, pe:
                return "ParserError: " + str(pe)

        if len(parse_tree) < 2:
                return quiz.translate(msgid='update_wiki_params',default='A quiz must have a title.')
        else:
                if str(parse_tree[0]) == 'quiz':                        # 1st tokeen must be quiz
                        del parse_tree[0]                                               # omit 1st token        
                        if type(parse_tree[0]) is str:
                                quiz.setTitle(parse_tree[0]); del(parse_tree[0])

                        # Keyword arguments, we have to check if there is a list and if this list
                        # starts with a key like ':key', otherwise it is something else ;)
                        if parse_tree and type(parse_tree[0]) is list and str(parse_tree[0][0]).startswith(':'):
                                args = parse_tree[0]
                                if atoms(args) % 2 == 0:                        # every keyword needs an argument
                                        while args:                                             # do as long as there are arguments left
                                                key,arg = str(args[0]),str(args[1]); del args[0],args[0]
                                                if key == ':desc':                      quiz.setDescription(arg)
                                                elif key == ':dir':                     quiz.setDirections(arg)
                                                elif key == ':rand':
                                                        if arg == 't':                  quiz.setRandomOrder(True)
                                                        else:                                   quiz.setRandomOrder(False)
                                                else:
                                                        return quiz.translate(msgid='update_wiki_args',default='Parameter error: ')+str(key)
                                else:
                                        return quiz.translate(msgid='update_wiki_args',default='Parameter error: ') + str(parse_tree[0])
                                del parse_tree[0]

                        quiz.reindexObject()

                        # Look for sub-elements if parse_tree is not empty, in  
                        # both ways we have to remove all sub-elements before.
                        quiz.manage_delObjects(quiz.contentIds())
                        if parse_tree:
                                return __updateElements(quiz,parse_tree)
                else:
                        return quiz.translate(msgid='update_wiki_quiz_begin',default='Syntax must begin with "(quiz ...".')

        return True


def __updateElements(parent,parse_tree):
        """Updates elements of a given object.

        This is done the brute force way, every content of 'parent' is deleted and
        rebuilt from the entries in 'parse_tree'. This may be improved in the future,
        but plone sucks at more sophisiticated content updates.

        Parameters:
                parent          - Element to update
                parse_tree      - A dictionary"""

        for elem in parse_tree:                                                         # Check all elements
                if type(elem) is list:                                                  # Elements must be lists
                        content_type = str(elem[0]); del elem[0]        # and should have a type

                        if content_type == 'group':                                     # Found a group
                                if parent.portal_type == 'ECQGroup':
                                        return parent.translate(msgid='update_wiki_element_group',default='A Group inside a group is not allowed: ') + str(elem)

                                # Care for the title
                                elem_title = 'group_' + str(time())     
                                if elem and type(elem[0]) is str:       elem_title = elem[0]; del elem[0]
                                # Create the group object
                                parent.invokeFactory(id=elem_title,type_name='ECQGroup')
                                group = getattr(parent,elem_title)
                                group.setTitle(elem_title)
                                # Keyword arguments, we have to check if there is a list and if this list
                                # starts with a key like ':key', otherwise it is something else ;)
                                if elem and type(elem[0]) is list and str(elem[0][0]).startswith(':'):
                                        args = elem[0]
                                        if atoms(args) % 2 == 0:                                # Every keyword needs an argument
                                                while args:                                                     # Do as long as there are arguments left
                                                        key,arg = str(args[0]),str(args[1]); del args[0],args[0]
                                                        if key == ':desc':              group.setDescription(arg)
                                                        elif key == ':dir':             group.setDirections(arg)
                                                        elif key == ':rand':
                                                                if arg == 't':          group.setRandomOrder(True)
                                                                else:                           group.setRandomOrder(False)
                                                        elif key == ':randnum': group.setNumberOfRandomQuestions(arg)
                                                        else:
                                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(key)
                                        else: 
                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(elem[0])
                                        del elem[0]
                                group.reindexObject()   

                                # Seach for sub-elements of this group if it is not empty.
                                if elem:
                                        retval = __updateElements(group,elem)   # Only return something if an error
                                        if retval != True:                                              # occured, otherwise keep going
                                                return retval

                        elif content_type == 'etq':                                             # Found an extended text question
                                # Care for the title
                                elem_title = 'etq_' + str(time())
                                if elem and type(elem[0]) is str:       elem_title = elem[0]; del elem[0]
                                # Create the extended text question object
                                parent.invokeFactory(id=elem_title,type_name='ECQExtendedTextQuestion')
                                quest = getattr(parent,elem_title)
                                quest.setTitle(elem_title)
                                if elem and type(elem[0]) is int:       quest.setPoints(elem[0]); del elem[0]
                                else:                                                           quest.setPoints(0)
                                if elem and type(elem[0]) is str:       quest.setQuestion(elem[0]); del elem[0]
                                else:                                                           quest.setQuestion('Question here!')
                                # Keyword arguments, we have to check if there is a list and if this list
                                # starts with a key like ':key', otherwise it is something else ;)
                                if elem and type(elem[0]) is list and str(elem[0][0]).startswith(':'):
                                        args = elem[0]
                                        if atoms(args) % 2 == 0:                                # Every keyword need an argument
                                                while args:                                                     # Do as long as there are arguments left
                                                        key,arg = str(args[0]),str(args[1]); del args[0],args[0]
                                                        if key == ':desc':              quest.setDescription(arg)
                                                        elif key == ':dir':     quest.setDirections(arg)
                                                        elif key == ':templ':   quest.setAnswerTemplate(arg)
                                                        elif key == ':len':     quest.setExpectedLength(arg)
                                                        else:
                                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(key)
                                        else:
                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(elem[0])
                                        del elem[0]
                                quest.reindexObject()

                        elif content_type == 'mcq':                                             # Found a mc question
                                # Care for the title
                                elem_title = 'mcq_' + str(time())
                                if elem and type(elem[0]) is str:       elem_title = elem[0]; del elem[0]
                                # Create the mc question object
                                parent.invokeFactory(id=elem_title,type_name='ECQMCQuestion')
                                quest = getattr(parent,elem_title)
                                quest.setTitle(elem_title)
                                if elem and type(elem[0]) is int:       quest.setPoints(elem[0]); del elem[0]
                                else:                                                           quest.setPoints(0)
                                if elem and type(elem[0]) is str:       quest.setQuestion(elem[0]); del elem[0]
                                else:                                                           quest.setQuestion('Question here!')
                                # Keyword arguments, we have to check if there is a list and if this list
                                # starts with a key like ':key', otherwise it is something else ;)
                                if elem and type(elem[0]) is list and str(elem[0][0]).startswith(':'):
                                        args = elem[0]
                                        if atoms(args) % 2 == 0:                                # Every keyword need an argument
                                                while args:                                                     # Do as long as there are arguments left
                                                        key,arg = str(args[0]),str(args[1]); del args[0],args[0]
                                                        if key == ':desc':              quest.setDescription(arg)
                                                        elif key == ':rand':
                                                                if arg == 't':          quest.setRandomOrder(True)
                                                                else:                           quest.setRandomOrder(False)
                                                        elif key == ':randnum': quest.setNumberOfRandomAnswers(arg)
                                                        elif key == ':multsel':
                                                                if arg == 't':          quest.setAllowMultipleSelection(True)
                                                                else:                           quest.setAllowMultipleSelection(False)  
                                                        elif key == ':tutor':
                                                                if arg == 't':          quest.setTutorGraded(True)
                                                                else:                           quest.setTutorGraded(False)
                                                        else:
                                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(key)
                                        else:
                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(elem[0])
                                        del elem[0]
                                quest.reindexObject()
                                # Look for answers if this mc question has some
                                if elem:                                                                        # Are there any answers ?
                                        for mcanswer in elem:                                   # Go over all answers
                                                answ_type = str(mcanswer[0]); del mcanswer[0]
                                                if answ_type == 't' or answ_type == 'f':
                                                        answ_title = 'mca_' + str(time())
                                                        quest.invokeFactory(id=answ_title,type_name='ECQMCAnswer')
                                                        answ = getattr(quest,answ_title)
                                                        if answ_type == 't':    answ.setCorrect(True)
                                                        else:                                   answ.setCorrect(False)
                                                        if mcanswer and type(mcanswer[0]) is str:                       
                                                                answ.setAnswer(mcanswer[0]); del mcanswer[0]
                                                        else:                                   answ.setAnswer('Answer here!')
                                                        if mcanswer and type(mcanswer[0]) is str:
                                                                answ.setComment(mcanswer[0]);del mcanswer[0]
                                                else:
                                                        return parent.translate(msgid='update_wiki_answer_unknown',default='Unknown answer type: ') + str(answ_type) + str(mcanswer)
                                        quest.reindexObject()

                        elif content_type == 'sq':                                              # Found a scale question
                                # Care for the title
                                elem_title = 'sq_' + str(time())
                                if elem and type(elem[0]) is str:       elem_title = elem[0]; del elem[0]
                                # Create the scale question object
                                parent.invokeFactory(id=elem_title,type_name='ECQScaleQuestion')
                                quest = getattr(parent,elem_title)
                                quest.setTitle(elem_title)
                                if elem and type(elem[0]) is int:       quest.setPoints(elem[0]); del elem[0]
                                else:                                                           quest.setPoints(0)
                                if elem and type(elem[0]) is str:       quest.setQuestion(elem[0]); del elem[0]
                                else:                                                           quest.setQuestion('Question here!')
                                # Keyword arguments, we have to check if there is a list and if this list
                                # starts with a key like ':key', otherwise it is something else ;)
                                if elem and type(elem[0]) is list and str(elem[0][0]).startswith(':'):
                                        args = elem[0]
                                        if atoms(args) % 2 == 0:                                # Every keyword need an argument
                                                while args:                                                     # Do as long as there are arguments left
                                                        key,arg = str(args[0]),str(args[1]); del args[0],args[0]
                                                        if key == ':desc':              quest.setDescription(arg)
                                                        elif key == ':lay':             
                                                                if arg == 'v':          quest.setChoiceLayout('vertical')
                                                                else:                           quest.setChoiceLayout('horizontal')
                                                        elif key == ':rand':
                                                                if arg == 't':          quest.setRandomOrder(True)
                                                                else:                           quest.setRandomOrder(False)
                                                        elif key == ':randnum': quest.setNumberOfRandomAnswers(arg)
                                                        else:
                                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(key)
                                        else:
                                                return parent.translate(msgid='update_wiki_args',default='Parameter error: ') + str(elem[0])
                                        del elem[0]
                                quest.reindexObject()
                                # Look for answers if this scale question has some
                                if elem:                                                                        # Are there any answers ?
                                        for sqanswer in elem:                                   # Go over all answers
                                                answ_score = str(sqanswer[0]); del sqanswer[0]
                                                if answ_score[-1:] == '%':
                                                        answ_title = 'sa_' + str(time())
                                                        quest.invokeFactory(id=answ_title,type_name='ECQScaleAnswer')
                                                        answ = getattr(quest,answ_title)
                                                        answ.setScore(answ_score)
                                                        if sqanswer and type(sqanswer[0]) is str:
                                                                answ.setAnswer(sqanswer[0]); del sqanswer[0]
                                                        else:                                   answ.setAnswer('Answer here!')
                                                        if sqanswer and type(sqanswer[0]) is str:
                                                                answ.setComment(sqanswer[0]); del sqanswer[0]
                                                else:
                                                        return parent.translate(msgid='update_wiki_answer_unknown',default='Unknown answer type: ') + str(answ_score) + str(sqanswer)
                                        quest.reindexObject()

                        else:                                                                                   # Found invalid element
                                return parent.translate(msgid='update_wiki_element_unknown',default='Unknown element type: ') + str(elem)
                else:                                                                                           # Found invalid element
                        return parent.translate(msgid='update_wiki_element_nested',default='Only nested elements allowed, not: ') + str(elem)

        return True                                                                                             # All done


### HELPERS ############################################


def atoms(collection):
        """Counts atomic elements in a list/dict/tuple...

        Parameters:
                collection      - The collection to search in"""
        count = 0
        for elem in collection:
                if type(elem) not in (dict,list,tuple):
                        count += 1
        return count


### IMPORT / EXPORT STUFF ##############################


def importQuiz(quiz, file):
        """Imports wiki-style data into an ECQuiz.

        Parameters:
                file            - An open file"""
        buffer = file.read()
        return updateQuiz(quiz,buffer)

def exportQuiz(quiz, filename):
        """Exports the given ECQuiz to a StringIO object and returns it.

        Parameters:
                filename        - A filename to save to"""
        package = StringIO()
        wikistyle = convertQuiz(quiz)
        package.write(wikistyle)
        return package


### CONVERT STUFF ######################################


def convertQuiz(quiz,verbose=True):
        """Examines an ECQuiz and returns it as wiki-syntax.

        The quiz object is recursivly traversed and a wiki-like syntax for printout
        or editing will be generated and returned.

        Parameters:
                quiz            - The ECQuiz object to convert
                verbose         - Use long syntax or not"""

        s = '(quiz "%s"\n' % quiz.Title()
        if verbose:
                s += '    (:desc "%s" :dir "%s"' % (quiz.Description(),quiz.directions)
                if quiz.randomOrder == True: 
                        s += ' :rand t'
                else:
                        s += ' :rand f'
                s += ')\n'
        else:
                pass
        for elem in quiz.objectValues():
                s += __convertElement(elem,verbose)
        s += ')\n'
        return s

def __convertElement(elem,verbose=True,indent=1):
        """Converts an subelement of an ECQuiz to wiki-syntax.

        Parameters:
                elem            - The sub-element of an ECQuiz to convert
                verbose         - Use long syntax or not
                indent          - Indentation level, don't touch ;)"""
        ind = indent*'    '
        s = ''

        # Check if we have found a group
        if elem.portal_type == 'ECQGroup':
                s += '%s(group "%s"\n' % (ind,elem.Title())
                if verbose:
                        s += '%s    (:desc "%s" :dir "%s"' % (ind,elem.Description(),elem.directions)
                        if elem.isRandomOrder():                        s += ' :rand t'
                        else:                                                           s += ' :rand f'
                        s += ' :randnum %d' % elem.numberOfRandomQuestions
                        s += ')\n'
                else:
                        pass
                for subElem in elem.objectValues():
                        s += __convertElement(subElem,verbose,indent+1)
                s += '%s)\n' % ind

        # Check if we have found a mc question  
        elif elem.portal_type == 'ECQMCQuestion':
                s += '%s(mcq "%s" %d "%s"\n' % (ind,elem.Title(),elem.points,elem.question)
                if verbose:
                        s += '%s    (:desc "%s"' % (ind,elem.Description())
                        if elem.isRandomOrder():                        s += ' :rand t'
                        else:                                                           s += ' :rand f'
                        s += ' :randnum %d' % elem.numberOfRandomAnswers
                        if elem.isAllowMultipleSelection():     s += ' :multsel t'
                        else:                                                           s += ' :multsel f'
                        if elem.isTutorGraded():                        s += ' :tutor t'
                        else:                                                           s += ' :tutor f'
                        s += ')\n'

                        for answ in elem.objectValues():
                                isCorrect = 'f'
                                if answ.correct: 
                                        isCorrect = 't'
                                s += '%s    (%s "%s" "%s")\n' % (ind,isCorrect,answ.answer,answ.comment)
                else:
                        pass
                s += '%s)\n' % ind

        # Check if we have found a scale question
        elif elem.portal_type == 'ECQScaleQuestion':
                s += '%s(sq "%s" %d "%s"\n' % (ind,elem.Title(),elem.points,elem.question)
                if verbose:
                        s += '%s    (:desc "%s"' % (ind,elem.Description())
                        if elem.choiceLayout == 'vertical':     s += ' :lay v'
                        else:                                                           s += ' :lay h'
                        if elem.isRandomOrder():                        s += ' :rand t'
                        else:                                                           s += ' :rand f'
                        s += ' :randnum %d' % elem.numberOfRandomAnswers
                        s += ')\n'

                        for answ in elem.objectValues():
                                score = str(int(answ.score))+'%'
                                s += '%s    (%s "%s" "%s")\n' % (ind,score,answ.answer,answ.comment)
                else:
                        pass
                s += '%s)\n' % ind      

        # Check if we have found a ext text question
        elif elem.portal_type == 'ECQExtendedTextQuestion':
                s += '%s(etq "%s" %d "%s"\n' % (ind,elem.Title(),elem.points,elem.question)
                if verbose:
                        s += '%s    (:desc "%s" :templ "%s"' % (ind,elem.Description(),elem.answerTemplate)
                        s += ' :len %d' % elem.expectedLength
                        s += ')\n'
                else:
                        pass
                s += '%s)\n' % ind

        return s
