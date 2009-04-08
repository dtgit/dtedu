# -*- coding: utf-8 -*-
# $Id: normPython.py,v 1.1 2007/07/02 14:40:25 peilicke Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

#===============================================================================
#Author: Christian Dervaric
#
#Description:
#This is a template to build normalizer for programming languages. It is based
#on the normalizing phase used in the YAP programs.
#
# For more information see: ...TODO:
#
#Steps:
#1. Remove all comments
#2. Remove all string constants
#3. Transform all normal letters to lower case
#4. map synonyms to more common forms (e.g. strncomp => strcomp or 
#    function => procedure
#5. Reorder functions according to their calling order. Then replace the first 
#    function call by the function body other calls of the function by the word 
#    FUN
#6. Delete all tokens that are not part of the target programming language
#
#How to Use:
# Copy this Template.
# Rename it e.g. normHaskell or normJava etc.
# Insert Descriptions and fill out the functions with the according code.
#===============================================================================

from Products.ECAssignmentBox.PlagDetector.errors import NoValidArgumentError
import re



#===============================================================================
#    GLOBAL PATTERNS, SYNONYMS AND KEYWORDS
#===============================================================================
#patterns to detect all comments
commentPatterns = ['#.*',                     # #...
                   '\"\"\"(.|\n)*?\"\"\"']    # """...""" multiline
#patterns to detect all string constants
stringConstantPatterns = ['\"(.|\n)*?\"',    # "..."    multiline
                           '\'(.|\n)*?\'']    # '...'    multiline
#synonyms
synonyms = {'\+=' : '=', '-=' : '=', '\*=' : '=', '/=' : '='                        #Assignments
            } #Comparisons
#Language Keywords
keywords = ['and', 'assert', 'break', 'class', 'continue', 'def', 
            'del', 'elif', 'else', 'except', 'exec', 'finally',  
            'for', 'from', 'global', 'if', 'import', 'in',
            'is', 'lambda', 'not', 'or', 'pass', 'print', 
            'raise', 'return', 'try', 'while', 'yield']
#own keywords for describing the structure
ownkeywords = ['BEGIN_METHOD', 'END_METHOD', 'TEST', 'ASSIGN', 
               'BEGIN_CLASS', 'END_CLASS', 'FUN', 'APPLY']
#patterns to apply ... TODO: beschreibung
patterns = {'[^=\n]+=' : 'ASSIGN ',#'[^=\n]+=[^=\n]+' : 'ASSIGN',    # ASSIGN ... = ...
            'if .*:' : 'if TEST',                 # if TEST   if ... :
            '(\w+\.)*\w+\((\s|,|\[|\]|\w|\w+\(.*\)|\n)*\)' : 'APPLY'  # APPLY  ...(...)
}    


def normalize(string, returnLinesForEachToken=False):
    """Normalizes the given string as python program in that way that 
        it extracts the structure. 
        
        It returns a string describing the program structure by special 
        structure tokens and a list containing the line number for each
        structure token in the original program code.
    """
    #check for valid string argument
    if string == '':
        return ''
    elif type(string) != type(''):
        raise NoValidArgumentError, 'Input must be of type String.'
    
    normalizedString = ''
    lineNrList = range(len(string.splitlines()))
    
    #Preprocesses string
    string = preprocess(string, lineNrList)
    
    #1. Remove all comments
    normalizedString = removeComments(string, lineNrList)
    
    #2. Remove all string constants
    normalizedString = removeStringConstants(normalizedString, lineNrList)
    
    #3. Transform all letters to lower case
    normalizedString = normalizedString.lower()
    
    #4. map synonyms
    normalizedString = mapSynonyms(normalizedString)
    
    #5. reorder functions and replace them firstly by their function body and afterwards by FUN
    normalizedString = reorderFunctions(normalizedString, lineNrList)
    
    #6. delete all tokens not part of the target language
    normalizedString = removeAllNonTargetLanguageToken(normalizedString, lineNrList)
    
    #return results
    if returnLinesForEachToken:
        return normalizedString, lineNrList
    else:
        return normalizedString

def removeComments(s, lineNrList):
    """Removes all comments in the given string s.
    """
    for pattern in commentPatterns:
        s = removePatternMatchesFromString(s, pattern, lineNrList)
    return s

def removeStringConstants(s, lineNrList):
    """Removes all string constants in the given string s.
    """
    for pattern in stringConstantPatterns:
        s = removePatternMatchesFromString(s, pattern, lineNrList)
    return s

def mapSynonyms(s):
    """Maps synonyms to more comon forms in the given string s.
    """
    for pattern in synonyms:
        s = re.sub(pattern, synonyms.get(pattern), s)
    return s

def reorderFunctions(s, lineNrList):
    """Reorders functions and replaces them firstly by their function body and 
        afterwards by 'FUN' in the given string s.
        
        Note: This method does not reorder the functions for now, because it seems
        not to be very helpful.
    """
    #===COLLECT NAMES, POSTIONS(START, END) OF CLASSES AND FUNCTIONS===
    #struct for functions -> name, posStart, posEnd, expanded, className
    class funStruct(object):
        name = ''
        posStart = 0
        posEnd = 0
        expanded = False
        className = None
        
    funcs = []    # list for all found functions
    #struct for classes -> name, posStart, posEnd
    class classStruct(object):
        name = ''
        posStart = 0
        posEnd = 0
        className = None
        
    classes = []    # list for all found classes
    
    #Patterns for functions and classes
    functionPattern = 'def\s+(\w+)\s*\(.*\):'    # def name(...):
    classPattern = 'class\s+(\w+)\s*\(.*\):'    # class name(...):
    
    #init for function and class search
    lines = s.splitlines()
    fun = funStruct()
    cl = classStruct()
    inDef = False
    funcWS = 0
    classWS = []
    inClass = []
    tmpClasses = []
    
    #walk through lines and get all functions and classes
    for lineNr in xrange(0, len(lines)):
        line = lines[lineNr]

        #while in function increment counter for endpos of the function
        if inDef and (funcWS < getFirstWhiteSpaces(line) or isEmptyLine(line)):
            fun.posEnd = lineNr
        else:
            if inDef: 
                funcs.append(fun)
                inDef = False
            
        #is there a start for function definition in this line
        funMatch = re.search(functionPattern, line)
        if funMatch:
            fun = funStruct()
            fun.name = funMatch.group(1)
            fun.posStart = lineNr
            fun.posEnd = lineNr
            inDef = True
            funcWS = getFirstWhiteSpaces(line)
            if inClass: fun.className = cl.name
            

        #while in class increment size of class
        for clNr in xrange(0, len(tmpClasses)):
            if inClass[clNr] and (classWS[clNr] < getFirstWhiteSpaces(line) or isEmptyLine(line)):
                tmpClasses[clNr].posEnd = lineNr
            else:
                if inClass[clNr]: 
                    classes.append(tmpClasses[clNr])
                    inClass[clNr] = False

        #is there a start for class definition in this line
        classMatch = re.search(classPattern, line)
        if classMatch:
            cl = classStruct()
            cl.name = classMatch.group(1)
            cl.posStart = lineNr
            cl.posEnd = lineNr
            classWs = getFirstWhiteSpaces(line)
            tmpClasses.append(cl)
            classWS.append(classWs)
            inClass.append(True)
        
        #if source file ends close still open methods and classes
        if lineNr == len(lines)-1:
            #close open function
            if inDef: funcs.append(fun)
            #close open classes
            for clNr in xrange(0, len(tmpClasses)):
                if inClass[clNr]: classes.append(tmpClasses[clNr])
    

    #===Mark start and ending of functions and classes===
    for f in funcs:
        lines[f.posStart] = re.sub(functionPattern, 'BEGIN_METHOD', lines[f.posStart])
        if isEmptyLine(lines[f.posEnd]):
            lines[f.posEnd] = 'END_METHOD'
        else: 
            lines[f.posEnd] = lines[f.posEnd] + '\nEND_METHOD'    #was ist wenn in selber zeile class def.?
            lineNrList[f.posEnd] = [lineNrList[f.posEnd], -1]#TODO: 25.01.07 add -1 as placeholder for new Line

    for c in classes:
        lines[c.posStart] = re.sub(classPattern, 'BEGIN_CLASS', lines[c.posStart])
        if isEmptyLine(lines[c.posEnd]):
            lines[c.posEnd] = 'END_CLASS'
        else: 
            lines[c.posEnd] = lines[c.posEnd] + '\nEND_CLASS'    #was ist wenn in selber zeile class def.?
            if type(lineNrList[c.posEnd]) == type([]):    #TODO: 250107
                lineNrList[c.posEnd].append(-1)
            else: lineNrList[c.posEnd] =  [lineNrList[c.posEnd], -1] #TODO: 25.01.07 add -1 as placeholder for new Line

    #===Replace all internal function calls: ===
    #    -> first appearance by method body, other appearances by FUN
    for lineNr in xrange(0, len(lines)):
        line = lines[lineNr]
        #if line contains methodname
        match = re.search('(\w+)\(.*\)', line)    #TODO: was ist mit mehr zeiligen Funktionsdefinitionen
        if match:
            #replace method call by method body
            body, start, end = getMethodBody(match.group(1), funcs, lines)
            if body:
#                print "BODY: ", match.group(1), start, end, end-start
                lines[lineNr] = re.sub(match.group(1)+'.*', '\n'+body, line)
                nr = lineNrList[lineNr]    #TODO: 250107 gesamter Abschnitt
                if body != 'FUN\n':
                    if type(nr) == type([]):
                        #lineNrList[lineNr] = nr+lineNrList[start:end]
                        bodyList = lineNrList[start:end+1]
                        bodyList.reverse()
                        for x in bodyList:
                            lineNrList[lineNr].insert(1, x)
                    else: lineNrList[lineNr] = [nr]+lineNrList[start:end+1]
                else:
                    if type(nr) == type([]):
                        lineNrList[lineNr] = nr.extend([-1, -1])#nr.append(-1)
                    else: lineNrList[lineNr] = [nr, -1, -1]#[nr, -1]
    
    #extend lists in lineNrList TODO: 250107 gesamter Abschnitt 
    #evtl. kann man den Abschnitt in den vorigen integrieren mit newlineNrList und list.extend(list)
    newlineNrList = lineNrList[:]
    del(lineNrList[0:len(lineNrList)])
    for l in expandList(newlineNrList):
        lineNrList.append(l)
#===============================================================================
#    for l in newlineNrList:
#        if type(l) == type([]):
#            lineNrList.extend(l)
#        else:
#            lineNrList.append(l)
#===============================================================================

    #recreate string from list of lines and return it
    #lines = [line+'\n' for line in lines]
    return '\n'.join(lines)+'\n'

def expandList(list):
    tmplist = []
    
    for l in list:
        if type(l) == type([]):
            tmplist.extend(expandList(l))
        else:
            tmplist.append(l)
            
    return tmplist

def getFirstWhiteSpaces(line):
    """Returns the number of whitespaces at the beginning of the string line."""
    return (len(line.expandtabs())-len(line.expandtabs().lstrip()))

def isEmptyLine(line):
    """Returns True if the string line only consists of whitespaces [' ','\n','\t', ...]."""
    #if line == '' or re.search('\s+', line):#if re.search('\s+', line):
    #if len([s for s in line if re.search('\s', line)]) == 0:    TODO: old version 17.01 13:04
    if len([s for s in line if re.search('\s', s)]) == len(line):
        return True
    else: return False
    
def getMethodBody(funName, funList, lines):
    """Gets the body of the method funName from lines and returns it 
        as a string.
    """
    f = None
    for fun in funList:
        if fun.name == funName:
            f = fun
            break
    if f:
        if f.expanded:
            return 'FUN\n', -1, -1
        else:
            f.expanded = True
            body = [lines[i]+'\n' for i in xrange(fun.posStart+1, fun.posEnd)]
            return ''.join(body), fun.posStart+1, fun.posEnd
    else:
        return None, -1, -1

def removeAllNonTargetLanguageToken(s, lineNrList):
    """Removes all tokens in the given string s which are not part of the target 
        language.
    """
    #replace patterns as defined in 'patterns'
    for pattern in patterns:
        #s = re.sub(pattern, patterns.get(pattern), s)
        s = replacePatternMatchesInString(s, pattern, patterns.get(pattern), lineNrList)
        
    #delete all non target language token,i.e. all tokens that are not in list keywords 
    #and additional all that are not in list ownkeywords
    lines = s.splitlines()
    sList = []
    tmplineNrList = lineNrList[:]
    del(lineNrList[0:len(lineNrList)])
    for lineNr in xrange(0, len(lines)):
        line = lines[lineNr]
        if not isEmptyLine(line):
            lineList = [s.rstrip(': ') for s in line.split() if s.rstrip(': ') in keywords or s.rstrip(': ') in ownkeywords]
            sList.extend(lineList)
            lineNrList.extend([tmplineNrList[lineNr] for s in lineList])
     
    #return string without leading and following whitespaces
    return " ".join(sList)


def preprocess(s, lineNrList):
    """Searches string s and looks for class and function definitions that
        are splitted over more than one line.
        This definition parts are put together in a single line and the string
        is returned.
    """
    lines = s.splitlines(True)
    lineNr = 0
    while lineNr < len(lines):
        if re.search('class\s+\w+\(', lines[lineNr]) or re.search('def\s+\w+\s*\(', lines[lineNr]):
            cnt = 0
            s = lines[lineNr].rstrip('\n ')
            #print lineNr, lines[lineNr]
            openP = countParenthesis(lines[lineNr])
            while openP != 0:
                cnt += 1
                openP += countParenthesis(lines[lineNr+cnt])
                s += ' '+lines[lineNr+cnt].rstrip('\n ')
                lines[lineNr+cnt] = '' #remove the newly empty lines by setting them to ''
            lines[lineNr] = s+'\n'
            del(lineNrList[lineNr+1: lineNr+cnt+1])#TODO: 250107 delete all empty lines that will be deleted
            lineNr += cnt+1 # Ende und so
            continue
        lineNr += 1
    return ''.join(lines)

def countParenthesis(string):
    """Counts parenthesises in the string s. Every open parenthesis '(' increments 
        the counter by one, every close decrements it by one.
        
        return int 
        if int == 0 -> no parents or as much '(' as')' 
        if int>0    -> more '(' than ')'
        if int<0    -> more ')' than '('
    """
    openP = 0
    for s in string:
        if s == '(':
            openP += 1
        elif s == ')':
            openP -= 1
    return openP

def removePatternMatchesFromString(s, pattern, lineNrList):
    """Removes the given pattern string in string s and adjusts
        lineNrList accordingly.
    """
    while True:
        m = re.search(pattern, s)
        if m:
            #remove lines from lineNrList
            cntNL = s[m.start():m.end()].count('\n')
            if cntNL > 0:
                start = s[:m.start()].count('\n')
                end = start + cntNL
                del(lineNrList[start:end])
            #remove m from s
            s = s[:m.start()]+s[m.end():]
        else:
            break
    return s

def replacePatternMatchesInString(s, pattern, replace, lineNrList):
    """Replaces the given 'pattern' by the 'replace' string in string s and
        adjusts the lineNrList accordingly.
    """    
    while True:
        m = re.search(pattern, s)
        if m:
            #remove lines from lineNrList
            cntNL = s[m.start():m.end()].count('\n')
            if cntNL > 0:
                start = s[:m.start()].count('\n')
                end = start + cntNL
                del(lineNrList[start:end])
            #remove m from s
            s = s[:m.start()]+replace+s[m.end():]
        else:
            break
    return s
